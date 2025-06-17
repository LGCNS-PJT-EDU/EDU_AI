from fastapi import APIRouter
from datetime import date
from app.utils.prometheus_metrics import daily_insert_total

router = APIRouter()

@router.post("/insert")
def test_insert(source: str = "feedback"):
    daily_insert_total.labels(source=source, date=str(date.today())).inc()
    return {"msg": f"{source} 삽입 카운터 증가"}
