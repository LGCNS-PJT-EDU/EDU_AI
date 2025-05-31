from app.clients import db_clients

async def get_recommended_contents_by_subject(subject_name: str):
    db = db_clients["recommendation"]

    results = await db.recommendation_content.find({"subject_name": subject_name}).to_list(length=None)
    return results
