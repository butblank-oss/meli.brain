"""나라장터 계약정보 수집(증분).

사용: python g2b_collect.py data [--recent 2]
- 인증키: 환경변수 G2B_KEY (GitHub Actions secret). 없으면 data/.key 파일.
- 2024년 1월부터 이번 달까지 중 최근 N개월만 다시 받아 data/items.jsonl.gz 에 합칩니다.
- 시니어 디지털 분류 규칙(rules.CATS)에 걸리는 계약만 저장합니다.
"""
import json, os, sys, time, gzip, re, ssl, calendar, datetime as dt
import urllib.parse, urllib.request, concurrent.futures as cf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rules import CATS

OUT = sys.argv[1]
RECENT = int(sys.argv[sys.argv.index("--recent") + 1]) if "--recent" in sys.argv else 2
KEY = os.environ.get("G2B_KEY") or open(os.path.join(OUT, ".key")).read().strip()
B = "https://apis.data.go.kr/1230000/ao/CntrctInfoService"
KW = ["치매", "인지", "두뇌", "뇌건강", "기억", "경로당", "돌봄로봇", "로봇", "안부",
      "어르신", "시니어", "노인", "헬스케어", "건강관리", "걸음", "손목닥터", "워크온",
      "비대면", "메타버스", "스마트돌봄"]
KST = dt.timezone(dt.timedelta(hours=9))
NOW = dt.datetime.now(KST)

ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None)
ctx = ssl.create_default_context(cafile=ca) if ca else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))

def months():
    out = []
    y, m = 2024, 1
    while (y, m) <= (NOW.year, NOW.month):
        last = calendar.monthrange(y, m)[1]
        end = min(dt.date(y, m, last), NOW.date())
        out.append((f"{y}{m:02d}01", end.strftime("%Y%m%d")))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out[-RECENT:]

def call(kind, kw, b, e, page):
    q = f"serviceKey={KEY}&numOfRows=999&pageNo={page}&type=json&inqryDiv=1&inqryBgnDate={b}&inqryEndDate={e}&cntrctNm={urllib.parse.quote(kw)}"
    url = f"{B}/getCntrctInfoList{kind}PPSSrch?{q}"
    err = None
    for a in range(8):
        try:
            with opener.open(url, timeout=60) as r:
                d = json.loads(r.read().decode("utf-8"))
            if "response" not in d:
                code = list(d.values())[0]["header"]["resultCode"]
                if code in ("03",):
                    return 0, []
                raise RuntimeError(str(d)[:200])
            body = d["response"]["body"]
            return int(body.get("totalCount") or 0), body.get("items") or []
        except Exception as ex:
            err = ex
            time.sleep(1.5 * (a + 1))
    raise RuntimeError(f"fail {kind} {kw} {b}: {err}")

def job(args):
    kind, kw, b, e = args
    tot, items = call(kind, kw, b, e, 1)
    page = 1
    while len(items) < tot:
        page += 1
        _, more = call(kind, kw, b, e, page)
        if not more:
            break
        items += more
    for it in items:
        it["_kind"] = kind
    return items

ms = months()
tasks = [(k, kw, b, e) for k in ("Servc", "Thng") for kw in KW for b, e in ms]
print("months", [m[0][:6] for m in ms], "tasks", len(tasks), flush=True)
cat_re = re.compile("|".join(f"(?:{p})" for _, p in CATS), re.I)
new, fails = {}, []
with cf.ThreadPoolExecutor(6) as ex:
    for fu in cf.as_completed([ex.submit(job, t) for t in tasks]):
        try:
            for it in fu.result():
                if cat_re.search(it.get("cntrctNm", "")):
                    new[it.get("untyCntrctNo") or it.get("cntrctNo")] = it
        except Exception as e2:
            fails.append(str(e2))
if fails:
    print("FAILED", len(fails), fails[:5])
    sys.exit(1)

path = os.path.join(OUT, "items.jsonl.gz")
old = {}
if os.path.exists(path):
    for line in gzip.open(path, "rt", encoding="utf-8"):
        it = json.loads(line)
        old[it.get("untyCntrctNo") or it.get("cntrctNo")] = it
added = len(set(new) - set(old))
old.update(new)
with gzip.open(path, "wt", encoding="utf-8") as f:
    for k in sorted(old):
        f.write(json.dumps(old[k], ensure_ascii=False) + "\n")
json.dump({"asof": NOW.strftime("%Y-%m-%d %H:%M"), "months": [m[0][:6] for m in ms], "fetched": len(new), "added": added, "total": len(old)},
          open(os.path.join(OUT, "asof.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("fetched", len(new), "added", added, "total", len(old))
