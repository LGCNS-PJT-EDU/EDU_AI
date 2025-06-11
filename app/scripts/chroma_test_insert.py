# scripts/chroma_test_insert.py
from app.utils.embed import embed_to_chroma

if __name__ == "__main__":
    embed_to_chroma(
        user_id="test_user_02",
        content="이건 AIOps 테스트 문서입니다.",
        source="aiops_test",
        source_id="manual_insert",
        metadata={"tag": "테스트", "importance": "high"}
    )
