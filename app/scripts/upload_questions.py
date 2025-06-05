import os
import json
import asyncio
from app.clients import db_clients


question_db = db_clients["ai_platform"]

async def upload_questions():
    # 현재 스크립트 기준 경로
    basedir = os.path.dirname(__file__)
    filepath = os.path.abspath(os.path.join(basedir, "../data/pre_post_questions.json"))

    with open(filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    await question_db.evaluation_questions.delete_many({})  # 옵션: 기존 삭제
    await question_db.evaluation_questions.insert_many(questions)
    print("문제 업로드 완료")

if __name__ == "__main__":
    asyncio.run(upload_questions())


