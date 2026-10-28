#!/usr/bin/env bash
# 나라장터에서 최근 N개월(기본 2)을 다시 불러와 지도 페이지를 새로 만듭니다.
set -euo pipefail
cd "$(dirname "$0")"
RECENT="${1:-2}"
python3 g2b_collect.py data --recent "$RECENT"
python3 g2b_classify.py data > /dev/null
python3 g2b_aggregate.py data > /dev/null
python3 build_map.py data/regional.json ../status.html > /dev/null
python3 vendors_page.py ../vendors.html > /dev/null
python3 export_csv.py ..
echo "done: $(cat data/asof.json)"
