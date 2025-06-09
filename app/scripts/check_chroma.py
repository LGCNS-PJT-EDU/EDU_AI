from langchain.vectorstores import Chroma

db = Chroma(persist_directory="chroma_store/recommend_contents", embedding_function=...)
print(" 총 문서 수:", db._collection.count())


