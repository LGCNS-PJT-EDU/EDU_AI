import asyncio
from app.clients import mongo_client, chroma_client
from app.utils.embed import embed_to_chroma  # 이 함수가 존재해야 합니다

async def manual_embed_test(user_id: str, source: str = "recommendation"):
    # Mongo에서 데이터 확인
    docs = await mongo_client.recommendation_content.find({"user_id": user_id}).to_list(length=100)
    print(f"[INFO] Fetched {len(docs)} documents for user_id={user_id} from Mongo")

    # 수동 임베딩 함수 실행
    if docs:
        await embed_to_chroma(source=source, user_id=user_id)
        print(f"[SUCCESS] embed_to_chroma() 실행 완료 for user_id={user_id}")
    else:
        print(f"[WARN] MongoDB에 user_id={user_id} 문서 없음")

# 실행
if __name__ == "__main__":
    asyncio.run(manual_embed_test(user_id="7"))
