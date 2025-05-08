# app/roadmap.py

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

def create_roadmap_vectorstore():
    loader = TextLoader("data/roadmap_documents/all_roadmaps.txt", encoding="utf-8")
    documents = loader.load()

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(documents)

    embedding = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(docs, embedding, persist_directory="chroma_store/roadmaps")

    vectordb.persist()
    return vectordb
