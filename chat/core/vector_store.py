# chat/core/vector_store.py

from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from chat.core.bedrock_embeddings import initialize_embedding_service

import os

CHROMA_PERSIST_DIRECTORY = "chroma_db"

def index_documents_in_chroma(texts: list[str], metadatas: list[dict], persist: bool = True):
    """
    Indexa documentos no ChromaDB com embeddings do Amazon Bedrock.
    """
    embedding_function = initialize_embedding_service().embeddings

    # Criação dos documentos com texto e metadados
    docs = [Document(page_content=text, metadata=meta) for text, meta in zip(texts, metadatas)]

    # Inicializa ou carrega o ChromaDB
    chroma = Chroma(
        embedding_function=embedding_function,
        persist_directory=CHROMA_PERSIST_DIRECTORY
    )

    # Adiciona os documentos ao vector store
    chroma.add_documents(documents=docs)

    if persist:
        chroma.persist()

    print(f"✔️ {len(docs)} documentos indexados no ChromaDB.")
