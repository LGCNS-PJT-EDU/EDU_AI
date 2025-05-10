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
