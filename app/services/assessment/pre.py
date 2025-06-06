from fastapi import HTTPException


async def level_to_string(level):
    if level == 1:
        return "novice"
    elif level == 2:
        return "amateur"
    elif level == 3:
        return "intermediate"
    elif level == 4:
        return "expert"
    elif level == 5:
        return "master"
    else:
        raise HTTPException(status_code=404, detail="Level out of range")