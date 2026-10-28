import json, re, sys, csv, collections

import gzip, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
from rules import SIDO, CATS, GOODS, EXCL

import importlib.util as _iu
_sp = _iu.spec_from_file_location("m", os.path.dirname(os.path.abspath(__file__)) + "/sgg_master.py"); _m = _iu.module_from_spec(_sp); _sp.loader.exec_module(_m)
_CNT = collections.Counter(g for v in _m.SGG.values() for g in v)
UNIQ = {g: sd for sd, v in _m.SGG.items() for g in v if _CNT[g] == 1 and not g.endswith("구")}

def region_from_name(nm):
    # 계약대행 등 수요기관명으로 지역을 못 찾을 때: 계약명 속 유일한 시·군 이름
    for tok in re.findall(r"(\S{1,4}?(?:시|군))", nm):
        if tok in UNIQ: return UNIQ[tok], tok
    return "", ""

def region(name):
    m = re.match(r"\s*전남광주통합특별시\s*(.*)", name)
    if m:
        g = re.match(r"(\S+?(?:시|군|구))(?:\s|$|보건|청)", m.group(1) + " ")
        sgg = g.group(1) if g else ""
        return ("광주" if sgg.endswith("구") else "전남"), sgg
    for short, pat in SIDO:
        m = re.match(rf"\s*({pat})\s*(.*)", name)
        if m:
            rest = m.group(2)
            g = re.match(r"(\S+?(?:시|군|구))(?:\s|$|보건|청)", rest + " ")
            sgg = g.group(1) if g else ""
            if short == "세종": sgg = ""
            return short, sgg
    return "", ""

def parse_list(s):
    out = []
    for part in re.findall(r"\[([^\]]*)\]", s or ""):
        out.append(part.split("^"))
    return out

rows, seen = [], set()
for line in gzip.open(f"{OUT}/items.jsonl.gz", "rt", encoding="utf-8"):
    it = json.loads(line)
    key = it.get("untyCntrctNo") or it.get("cntrctNo")
    if key in seen:
        continue
    seen.add(key)
    nm = it.get("cntrctNm", "")
    if re.search(EXCL, nm):
        continue
    if re.search(r"치매", nm) and re.search(r"(교재|교구|물품|소모품|간식|다과|기념품|리플렛|책자|티셔츠|가방|위탁 운영|위탁운영|인건비|운영 위탁|센터 운영|쉼터|가족|실종|배회|인식표|지문)", nm) and not re.search(r"(앱|어플|디지털|VR|AI|태블릿|스마트|훈련 프로그램|인지훈련|콘텐츠|플랫폼|로봇)", nm):
        continue
    cat = next((c for c, p in CATS if re.search(p, nm, re.I)), None)
    if not cat:
        continue
    if re.search(GOODS, nm) and not re.search(r"워크온|손목닥터", nm):
        continue  # 일반 물품(가전·경로당 비품·실종예방 태그·경품·의약품 등)
    if cat == "인지훈련·치매예방" and re.search(r"연구\s*용역|연구용역|원료|초등|코딩로봇|전문가 양성|인식개선|디지털타운|건강돌봄|주거환경|미션 성공물품", nm):
        continue  # 인지훈련이 아닌 치매 관련 사업(연구·인식개선·돌봄 모니터링 등)
    dm = parse_list(it.get("dminsttList"))
    dname = dm[0][2] if dm and len(dm[0]) > 2 else ""
    dtype = dm[0][3] if dm and len(dm[0]) > 3 else ""
    inst = dname or it.get("cntrctInsttNm", "")
    if re.search(r"학교|초등|중학|고등|유치원|교육청|교육지원청|교육원|과학관|대학교", inst):
        continue
    sido, sgg = region(inst)
    if not sido:
        sido, sgg = region(it.get("cntrctInsttNm", ""))
    if not sido:
        sido, sgg = region_from_name(nm)
    if not sido:
        continue  # 지역 판별 불가(중앙부처·공공기관 등)
    corp = parse_list(it.get("corpList"))
    vendor = corp[0][3] if corp and len(corp[0]) > 3 else ""
    amt = max(int(it.get("totCntrctAmt") or 0), int(it.get("thtmCntrctAmt") or 0))
    rows.append(dict(시도=sido, 시군구=sgg or "광역", 수요기관=inst, 기관구분=dtype, 유형=cat,
                     계약명=nm, 업체=vendor, 금액=amt, 계약일=it.get("cntrctCnclsDate", ""),
                     방법=it.get("cntrctCnclsMthdNm", ""), 구분=it["_kind"],
                     링크=it.get("cntrctDtlInfoUrl", "")))

rows.sort(key=lambda r: (r["시도"], r["시군구"], r["유형"], r["계약일"]))
with open(f"{OUT}/classified.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print("rows", len(rows))
c = collections.Counter((r["유형"]) for r in rows); print(c)
print(collections.Counter(r["시도"] for r in rows))
