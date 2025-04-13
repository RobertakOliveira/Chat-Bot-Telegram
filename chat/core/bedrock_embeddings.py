# chat/core/bedrock_embeddings.py
"""
Implementação do gerador de embeddings usando Bedrock.

Agora integrado diretamente com ChromaDB.
"""
import time
import logging
from typing import List
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, AWS_REGION
from chat.utils.config import config


class BedrockEmbeddingHandler:
    """Gera embeddings usando Bedrock para uso com ChromaDB"""

    def __init__(self):
        self.embeddings = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id=config.BEDROCK_MODEL_ID,
            region_name=AWS_REGION
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos de uma vez.
        Retorna lista de embeddings prontos para o ChromaDB.
        """
        start_time = time.time()

        try:
            embeddings = self.embeddings.embed_documents(texts)
            processing_time = (time.time() - start_time) * 1000

            logging.info(
                f"Generated {len(embeddings)} embeddings | "
                f"Avg time: {processing_time/len(texts):.2f}ms per text | "
                f"Dimensions: {len(embeddings[0]) if embeddings else 0}"
            )

            return embeddings

        except Exception as e:
            logging.error(f"Falha na geração de embedding: {str(e)}")
            raise

    def embed_documents(self, documents: List[Document]) -> List[Document]:
        """Novo: Gera embeddings para uma lista de LangChain Documents"""
        texts = [doc.page_content for doc in documents]
        embeddings = self.generate_embeddings(texts)

        # Adiciona embeddings aos metadados
        for doc, embedding in zip(documents, embeddings):
            doc.metadata["embedding"] = embedding

        return documents


def initialize_embedding_service():
    """Inicializa o serviço de embeddings"""
    return BedrockEmbeddingHandler()
