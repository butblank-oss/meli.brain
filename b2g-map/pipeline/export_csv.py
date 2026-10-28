"""regional.json -> data.csv(지역별 묶음), contracts.csv(계약별)"""
import json, csv, os, sys
BASE = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]
d = json.load(open(BASE + "/data/regional.json", encoding="utf-8"))
w = csv.writer(open(OUT + "/contracts.csv", "w", encoding="utf-8-sig", newline=""))
w.writerow(["시도", "시군구", "유형", "서비스", "계약일", "구분", "방법", "계약명", "금액(원)", "원문"])
for g in d:
    for c in g.get("계약", []):
        w.writerow([g["시도"], g["시군구"], g["유형"], g["서비스"], c[0], c[3], c[4], c[1], c[2], c[5]])
cols = ["시도", "시군구", "유형", "서비스", "업체", "건수", "금액", "최근", "출처", "링크", "예시"]
w2 = csv.writer(open(OUT + "/data.csv", "w", encoding="utf-8-sig", newline="")); w2.writerow(cols)
for g in sorted(d, key=lambda g: (g["시도"], g["시군구"], g["유형"])):
    w2.writerow([g.get(c, "") for c in cols])
print("csv ok")
