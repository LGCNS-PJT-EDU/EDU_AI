import json
import re
from datetime import date


async def build_feedback(data, feedback_text):
    try:
        text_reg = feedback_text.strip()
        text_reg = re.sub(r"^```json\s*|\s*```$", "", text_reg)
        match = re.search(r"\{.*\}", text_reg, re.DOTALL)
        if match:
            text_reg = match.group(0)

        parsed = json.loads(text_reg)
        info = parsed["info"]
        scores = parsed["scores"]
        feedback = parsed["feedback"]

    except json.JSONDecodeError:
        info = {
            "userId": data.user_id,
            "date": date.today().isoformat(),
            "subject": data.subject
        }
        scores = {
            **data.scores,
        }
        scores["total"] = sum(scores.values())
        feedback = {
            "strength": {},
            "weakness": {},
            "final": feedback_text
        }
    return feedback, info, scores