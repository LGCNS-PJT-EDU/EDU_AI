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


async def get_post_assessments(data, subject_id):
    post_assessments = []
    for k, a in data.items():
        if not k.startswith("post_assessments_"):
            continue
        try:
            n = int(k.rsplit("_", 1)[-1])
            sid = int(a.get("subject", {}).get("subjectId", -1))
        except (ValueError, TypeError):
            continue
        if sid == subject_id:
            post_assessments.append((n, a))
    post_assessments.sort(key=lambda x: x[0])
    return post_assessments