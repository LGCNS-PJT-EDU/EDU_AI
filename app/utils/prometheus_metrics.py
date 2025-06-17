from prometheus_client import REGISTRY, Counter

# 이미 등록된 경우 가져오기
if "daily_insert_total" in REGISTRY._names_to_collectors:
    daily_insert_total = REGISTRY._names_to_collectors["daily_insert_total"]
else:
    daily_insert_total = Counter(
        "daily_insert_total",
        "일일 문서 삽입 수",
        ["source", "date"]
    )
