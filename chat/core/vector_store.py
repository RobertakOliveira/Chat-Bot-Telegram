# chat/core/vector_store.py

from langchain_chroma import Chroma
from langchain.schema import Document
from chat.core.bedrock_embeddings import initialize_embedding_service
from chat.utils.logger import get_logger
import os

logger = get_logger("vector_store")

CHROMA_PERSIST_DIRECTORY = "chroma_db"

def index_documents_in_chroma(texts: list[str], metadatas: list[dict], persist: bool = True):
    """
    Indexa documentos no ChromaDB com embeddings do Amazon Bedrock.
    """
    embedding_function = initialize_embedding_service().embeddings

    # Criação dos documentos com texto e metadados, garantindo o campo '_type'
    docs = []
    for text, meta in zip(texts, metadatas):
        if not isinstance(meta, dict):
            meta = {}
        if "_type" not in meta:
            meta["_type"] = "document"
        docs.append(Document(page_content=text, metadata=meta))

    # Inicializa ou carrega o ChromaDB
    chroma = Chroma(
        embedding_function=embedding_function,
        persist_directory=CHROMA_PERSIST_DIRECTORY
    )

    # Adiciona os documentos ao vector store
    chroma.add_documents(documents=docs)

    # Remova a chamada a persist(), pois a nova versão não a possui
    # if persist:
    #    chroma.persist()
    logger.info("✅ Documentos indexados no ChromaDB.")
    print(f"✔️ {len(docs)} documentos indexados no ChromaDB.")



# from chromadb import Client

def retrieve_documents(query_embedding: list[float], k: int = 5):
    """
    Recupera os documentos mais relevantes para o embedding da pergunta, sem considerar o case_id.
    """
    logger.info(f"🔎 Caminho do diretório de persistência do Chroma: {CHROMA_PERSIST_DIRECTORY}")
    logger.info(f"📂 Arquivos no diretório de embeddings: {os.listdir(CHROMA_PERSIST_DIRECTORY)}")

    # Inicializa a função de embedding
    embedding_function = initialize_embedding_service().embeddings

    # Inicializa o Chroma
    chroma = Chroma(
        embedding_function=embedding_function,
        persist_directory=CHROMA_PERSIST_DIRECTORY
    )

    # Realiza a busca dos documentos mais semelhantes
    results = chroma.similarity_search_by_vector(query_embedding, k=k)

    # Verifica se algum documento foi encontrado
    if not results:
        logger.warning("⚠️ Nenhum documento encontrado para a consulta!")

    # Log para inspecionar os documentos e seus metadados
    for i, doc in enumerate(results):
        logger.debug(f"Documento {i}: conteúdo={doc.page_content}")
        logger.debug(f"Documento {i} metadados={doc.metadata}")

    return [doc.page_content for doc in results]
