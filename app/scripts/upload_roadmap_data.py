from pathlib import Path
import json
import asyncio

async def upload_roadmap_data():
    file_path = Path(__file__).parent.parent / "services" / "chroma_roadmap_docs_full.json"
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} 파일이 존재하지 않습니다!")

    with open(file_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    print(f"총 {len(raw_items)}개의 문서가 로드되었습니다!")

if __name__ == "__main__":
    asyncio.run(upload_roadmap_data())
