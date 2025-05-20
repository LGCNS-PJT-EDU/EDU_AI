# app/utils/level_utils.py

def calculate_level_from_answers(answers: dict) -> int:
  
    score = 0
    for key, value in answers.items():
        if isinstance(value, str) and value.upper() == "Y":
            score += 1

    if score <= 1:
        return 0  # 초급
    elif score <= 3:
        return 1  # 기초
    elif score == 4:
        return 2  # 중급
    else:
        return 3  # 상급


def normalize_duration(duration_str: str) -> float:
    if "~ 1시간" in duration_str:
        return 1
    elif "1시간 ~ 3시간" in duration_str:
        return 2
    elif "3시간 ~ 5시간" in duration_str:
        return 4
    elif "5시간 ~ 10시간" in duration_str:
        return 7.5
    elif "10시간" in duration_str:
        return 12
    else:
        return 1.0  # fallback