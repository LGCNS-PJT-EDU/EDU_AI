import random
from typing import List, Dict
from app.clients import db_clients
from app.services.assessment.common import safe_sample


interview_client = db_clients["ai_interview"]

async def get_questions_by_sub_id(subject_name: str, num_questions: int) -> List[Dict]:
    q = await interview_client.db[subject_name].find().to_list(length=1000)

    # 랜덤 샘플링 및 포맷 정제
    questions = safe_sample(q, num_questions)
    return questions
