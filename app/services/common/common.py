from fastapi import HTTPException

from app.clients import db_clients


question_db = db_clients["ai_platform"]
user_db = db_clients["user"]


async def subject_id_to_name(subject_id):
    tech_map = await question_db.techMap.find_one({})
    if not tech_map:
        raise HTTPException(status_code=404, detail="Can't find data")
    subject_name = tech_map.get(str(subject_id))
    if not subject_name:
        raise HTTPException(status_code=404, detail="Such subject not exist")
    return subject_name


async def get_user(user_id):
    user = await user_db.user_profile.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user