from langchain_chroma import Chroma
from langchain.schema import Document
from chat.core.bedrock_embeddings import initialize_embedding_service
from chat.utils.logger import get_logger
import os

logger = get_logger("vector_store")

CHROMA_PERSIST_DIRECTORY = "chroma_db"

def initialize_chroma_instance(collection_name: str):
    """
    Inicializa e retorna uma instância de Chroma (já representa a coleção).
    """
    embedding_function = initialize_embedding_service().embeddings
    chroma = Chroma(
        embedding_function=embedding_function,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        collection_name=collection_name
    )
    return chroma

def index_documents_in_chroma(texts: list[str], metadatas: list[dict], case_id: str, collection_name: str, persist: bool = True):
    embedding_function = initialize_embedding_service().embeddings

    docs = []
    for text, meta in zip(texts, metadatas):
        if not isinstance(meta, dict):
            meta = {}
        meta.setdefault("_type", "document")
        meta["case_id"] = case_id
        docs.append(Document(page_content=text, metadata=meta))

    # Inicializa o cliente Chroma como persistente
    chroma = Chroma(
        embedding_function=embedding_function,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        collection_name=collection_name  # Passando o nome da coleção
    )

    # Adiciona os documentos à coleção
    chroma.add_documents(documents=docs)

    # A persistência será automática quando o cliente for persistente, não é mais necessário chamar `persist()`
    logger.info(f"✅ Documentos do caso '{case_id}' indexados na coleção '{collection_name}'.")
    print(f"✔️ {len(docs)} documentos indexados para o caso {case_id} na coleção {collection_name}.")