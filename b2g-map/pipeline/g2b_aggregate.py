import csv, re, json, sys, collections

OUT = sys.argv[1]
rows = list(csv.DictReader(open(f"{OUT}/classified.csv", encoding="utf-8-sig")))

def label(r):
    n, v, c = r["계약명"], r["업체"], r["유형"]
    v2 = re.sub(r"주식회사|\(주\)|㈜|재단법인|사단법인|\s+", "", v)
    if "워크온" in n or "스왈라비" in v: return "워크온 걷기챌린지", "스왈라비"
    if "손목닥터" in n: return "손목닥터9988", v2
    if re.search(r"AI.{0,3}I[oO0][tT]|AI.{0,3}lo[tT]|AI\.LOT", n) and re.search(r"어르신|노인", n):
        if re.search(r"스피커", n) or "행복커넥트" in v: return "AI스피커(어르신 건강관리사업)", v2
        return "AI·IoT 어르신건강관리(정부사업)", "다수 납품업체"
    if re.search(r"모바일\s*헬스", n): return "모바일헬스케어(정부사업)", "다수 납품업체"
    if "행복커넥트" in v: return "AI스피커 돌봄(SKT·행복커넥트)", v2
    if re.search(r"케어콜|클로바", n) or "세종네트웍스" in v: return "클로바 케어콜(네이버)", v2
    if "효돌" in v or "효돌" in n: return "효돌 돌봄로봇", "효돌"
    if "원더풀플랫폼" in v or "다솜" in n: return "다솜 돌봄로봇", "원더풀플랫폼"
    if "미스터마인드" in v: return "AI 돌봄인형(미스터마인드)", "미스터마인드"
    if "원메딕스" in v: return "맬리브레인", "원메딕스"
    if "펀웨이브" in v: return "기억하리", "펀웨이브"
    if "하야트" in v: return "모바일 AI 치매예방 플랫폼(하야트)", "하야트"
    if "대교" in v: return "대교 인지강화 프로그램(대면)", v2
    if c == "스마트경로당": return f"스마트경로당({v2})", v2
    if c == "AI돌봄·안부": return f"AI안부·돌봄({v2})", v2
    if c == "돌봄로봇": return f"돌봄로봇({v2})", v2
    if "기억산책" in v: return "기억담기 등 인지훈련 앱 구축(기억산책)", "기억산책"
    if "로완" in v: return "슈퍼브레인(로완)", "로완"
    if c == "인지훈련·치매예방":
        if re.search(r"앱|어플|모바일|디지털|VR|AI|플랫폼|전산화|시스템|태블릿|스마트|로봇|장비|기기|콘텐츠|프로그램 운영|프로그램 및|용역", n):
            return f"인지훈련({v2})", v2
        return "치매예방 교구·교재 구매", "다수 납품업체"
    if c == "걸음·건강관리": return f"걷기·건강관리({v2})", v2
    return f"{c}({v2})", v2

agg = collections.OrderedDict()
seen=set()
for r in rows:
    dk=(r["수요기관"],r["계약일"],r["계약명"].strip(),r["금액"])
    if dk in seen: continue
    seen.add(dk)
    lab, vend = label(r)
    if "정부사업" in lab or lab == "AI스피커(어르신 건강관리사업)":
        continue  # 정부사업(AI·IoT 어르신건강관리, 모바일헬스케어) 기기 구매는 제외
    k = (r["시도"], r["시군구"], r["유형"], lab)
    a = agg.setdefault(k, dict(시도=r["시도"], 시군구=r["시군구"], 유형=r["유형"], 서비스=lab, 업체=vend,
                               건수=0, 금액=0, 최근=r["계약일"], 예시=r["계약명"], 출처="나라장터", 링크=r["링크"], 계약=[]))
    a["건수"] += 1; a["금액"] += int(r["금액"] or 0)
    a["계약"].append([r["계약일"], r["계약명"].strip(), int(r["금액"] or 0), ("물품" if r["구분"]=="Thng" else "용역"), r["방법"], r["링크"]])
    if r["계약일"] > a["최근"]:
        a["최근"], a["예시"], a["링크"] = r["계약일"], r["계약명"], r["링크"]

# news table
tbl = open(f"{OUT}/news_table.md", encoding="utf-8").read()
TYPEMAP = {"인지훈련": "인지훈련·치매예방", "선별검사": "인지훈련·치매예방", "걸음·건강관리": "걸음·건강관리",
           "AI돌봄·안부": "AI돌봄·안부", "돌봄로봇": "돌봄로봇", "스마트경로당": "스마트경로당"}
news = []
for line in tbl.splitlines():
    if not line.startswith("| ") or line.startswith("| 시도") or line.startswith("|---"):
        continue
    c = [x.strip() for x in line.strip("|").split("|")]
    if len(c) < 8: continue
    sido, sgg, name, typ, org, vend, yr, url = c[:8]
    news.append(dict(시도=sido, 시군구=("광역" if "광역" in sgg else sgg), 유형=TYPEMAP.get(typ, typ),
                     서비스=name, 업체=vend, 건수="", 금액="", 최근=yr, 예시=org, 출처="기사·공식자료", 링크=url))
news.append(dict(시도="인천", 시군구="남동구", 유형="인지훈련·치매예방", 서비스="맬리브레인 스마트 어플 치매예방교실",
                 업체="원메딕스", 건수="", 금액="", 최근="2026", 예시="남동구보건소",
                 출처="기사·공식자료", 링크="https://www.naewoeilbo.com/news/articleView.html?idxno=2410852"))

items = list(agg.values()) + news
json.dump(items, open(f"{OUT}/regional.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(agg), "contract groups,", len(news), "news")
cnt = collections.Counter(i["서비스"] for i in agg.values())
print(cnt.most_common(25))
