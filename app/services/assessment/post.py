from app.clients.mongodb import db


async def generate_key(user):
    profile = await db.user_profiles.find_one(
        {"user_id": user["user_id"]},
        {"_id": False, **{f: False for f in ["user_id", "pre_assessment"]}}
    )

    existing = [k for k in profile.keys() if k.startswith("post_assessments_")]
    next_idx = len(existing) + 1

    new_key = f"post_assessments_{next_idx}"
    return new_key