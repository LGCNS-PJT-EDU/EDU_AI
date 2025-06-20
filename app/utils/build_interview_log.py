from datetime import datetime

def build_interview_log(user_id: str, question_id: str, question: str, answer: str, evaluation: dict):
    return {
        "user_id": user_id,
        "question_id": question_id,
        "question": question,
        "answer": answer,
        "evaluation": {
            "logic": evaluation.get("logic", 0),
            "accuracy": evaluation.get("accuracy", 0),
            "clarity": evaluation.get("clarity", 0),
            "terms": evaluation.get("terms", 0),
            "overall_comment": evaluation.get("overall_comment", "")
        },
        "timestamp": datetime.now().isoformat()
    }
