# chat/core/retriever.py
from langchain_chroma import Chroma
from typing import List, Dict
from chat.core.bedrock_embeddings import initialize_embedding_service
from chat.utils.config import config
from chat.utils.logger import get_logger
import time

logger = get_logger("retriever")

class ChromaRetriever:
    def __init__(self, collection_name: str = "collection_89299"):
        self.embedding_function = initialize_embedding_service().embeddings
        self.persist_directory = config.CHROMA_DB_PATH
        self.collection_name = collection_name
        
        self.chroma = Chroma(
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )
        logger.info(f"🚀 Retriever inicializado com coleção: '{self.collection_name}'")

    def retrieve_documents(self, query_embedding: List[float], doc_type: str = None, case_id: str = None, n_results: int = 3) -> List[Dict]:
        try:
            start_time = time.time()
            logger.info(f"🔎 Iniciando busca de documentos... Embedding recebido com {len(query_embedding)} dimensões.")

            filters = {}

            if doc_type and doc_type.lower() == "outro":
                doc_type = None
            if case_id and case_id.lower() == "outro":
                case_id = None

            if doc_type and case_id:
                filters = {
                    "$and": [
                        {"doc_type": {"$eq": doc_type}},
                        {"case_id": {"$eq": case_id}}
                    ]
                }
            elif doc_type:
                filters = {"doc_type": {"$eq": doc_type}}
            elif case_id:
                filters = {"case_id": {"$eq": case_id}}

            if not filters:
                filters = None

            logger.info(f"🛠️ Filtros aplicados: {filters}")

            results = self.chroma._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filters
            )

            documents = []
            score_threshold = 1.7  # 🎯 Definindo o limite máximo permitido

            for ids, distances, metadatas, documents_text in zip(
                results['ids'], 
                results['distances'], 
                results['metadatas'], 
                results['documents']
            ):
                for id_, distance, metadata, text in zip(ids, distances, metadatas, documents_text):
                    if distance <= score_threshold:
                        logger.info(f"✅ Documento '{id_}' aceito | Score: {distance:.4f}")
                        logger.info(f"🧾 Metadados: {metadata}")
                        logger.info(f"📄 Conteúdo (início): {text}...\n")
                        documents.append({
                            'id': id_,
                            'score': distance,
                            'metadata': metadata or {},
                            'content': text
                        })
                    else:
                        logger.info(f"🚫 Documento '{id_}' filtrado | Score: {distance:.4f} acima do threshold ({score_threshold})")

            elapsed_time = time.time() - start_time

            if documents:
                logger.info(f"📄 {len(documents)} documentos relevantes encontrados.")
            else:
                logger.warning(f"⚠️ Nenhum documento relevante encontrado.")

            logger.info(f"⏱️ Tempo de busca: {elapsed_time:.2f} segundos.")

            return documents

        except Exception as e:
            logger.error(f"❌ Erro ao recuperar documentos: {str(e)}")
            raise