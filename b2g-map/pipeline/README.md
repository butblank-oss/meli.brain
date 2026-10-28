# b2g-map 데이터 파이프라인

나라장터 계약정보 API(조달청)에서 시니어 디지털 서비스 계약을 모아 `status.html`(전체 현황), `vendors.html`(경쟁 서비스)을 만듭니다.

- 다시 불러오기: GitHub Actions 「b2g-refresh」 → Run workflow. 실행한 시점 기준으로 최근 N개월(기본 2)을 다시 받아 합치고 페이지를 새로 만듭니다.
- 인증키: 저장소 Settings → Secrets and variables → Actions 에 `G2B_KEY` 로 등록합니다. 파일로 커밋하지 않습니다.
- 로컬 실행: `G2B_KEY=... ./run.sh 2`

| 파일 | 하는 일 |
|---|---|
| g2b_collect.py | 키워드 20개 × 최근 N개월 수집, 분류 규칙에 걸리는 계약만 data/items.jsonl.gz 에 합침 |
| rules.py | 분류 규칙(유형, 제외 단어, 일반 물품) |
| g2b_classify.py | 지역(시·도/시·군·구)과 유형 판별 → data/classified.csv |
| g2b_aggregate.py | 서비스별로 묶고 기사 자료(data/news_table.md) 합침 → data/regional.json |
| build_map.py / vendors_page.py | 페이지 생성 |
| export_csv.py | data.csv, contracts.csv |
