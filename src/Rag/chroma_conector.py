from Rag.config.config import Config
from langchain_chroma import Chroma
from chromadb import PersistentClient

def connect_chroma(embeddings):
    client = PersistentClient(path=Config.CHROMA_DIR)
    return Chroma(
        collection_name=Config.COLLECTION_NAME,
        embedding_function=embeddings,
        client=client
    )
