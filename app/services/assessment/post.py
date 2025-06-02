from app.clients import db_clients


assessment_db = db_clients["assessment"]
user_db = db_clients["user"]

async def generate_key(user):
    post_results = await assessment_db.post_result.find_one(
        {
            "userId": user["user_id"]
        }
    )

    next_idx = 1 if post_results is None else sum(1 for k in post_results.keys() if k.startswith("post_assessments_")) + 1

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