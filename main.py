from fastapi import FastAPI
from pydantic import BaseModel
from mongo_feedback import save_feedback

app = FastAPI()

class FeedbackContent(BaseModel):
    user_id: str
    voice_file: str
    content: dict

@app.post("/feedback")
async def upload_feedback(data: FeedbackContent):
    await save_feedback(data.user_id, data.content, data.voice_file)
    return {"message": "Feedback saved"}
