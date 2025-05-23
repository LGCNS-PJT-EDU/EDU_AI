from fastapi import HTTPException

from app.clients.mongodb import db


async def subject_id_to_name(subject_id):
    tech_map = await db.techMap.find_one({})
    if not tech_map:
        raise HTTPException(status_code=404, detail="Can't find data")
    subject_name = tech_map.get(str(subject_id))
    if not subject_name:
        raise HTTPException(status_code=404, detail="Such subject not exist")
    return subject_name