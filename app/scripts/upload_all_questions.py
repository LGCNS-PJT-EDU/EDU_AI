import os
import json
from pymongo import MongoClient

# MongoDB 연결
client = MongoClient("mongodb://localhost:27017")
db = client["ai_platform"]
collection = db["evaluation_questions"]

# 난이도 변환
def convert_difficulty(kor):
    return {
        "하": "low",
        "중": "medium",
        "상": "high"
    }.get(kor.strip(), "medium")

# 개별 업로드
def upload_json_file(filepath):
    filename = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    subject = filename.replace("_평가문제.json", "").replace("_", " ").strip()

    for i, q in enumerate(questions):
        doc = {
            "question_id": f"{subject.lower().replace(' ', '_')}_{i:03}",
            "subject": subject,
            "chapter": q["chapterName"],
            "difficulty": convert_difficulty(q["difficulty"]),
            "question": q["question"],
            "options": [q["option1"], q["option2"], q["option3"], q["option4"]],
            "answer_index": q["answerIndex"]
        }
        collection.update_one({"question_id": doc["question_id"]}, {"$set": doc}, upsert=True)

    print(f" {filename} → {len(questions)}개 업로드 완료")

# 전체 폴더 업로드
def upload_all_from_folder(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    for f in files:
        upload_json_file(os.path.join(folder_path, f))

# 실행
if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    folder = os.path.abspath(os.path.join(base_dir, "../../questions_folder"))
    upload_all_from_folder(folder)

