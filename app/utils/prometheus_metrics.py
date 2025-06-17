# app/utils/prometheus_metrics.py

from prometheus_client import Counter
from datetime import date

# 일일 삽입 수 추적
daily_insert_total = Counter(
    "daily_insert_total",
    "일일 문서 삽입 수",
    ["source", "date"]
)
