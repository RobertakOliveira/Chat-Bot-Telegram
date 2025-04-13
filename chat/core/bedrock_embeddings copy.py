# chat/core/bedrock_embeddings.py
import time
import logging
import datetime
from typing import List
from langchain_core.documents import Document
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, AWS_REGION
from chat.utils.config import bedrock_config


class BedrockEmbeddingHandler:
    """Otimizado para documentos jurídicos em EC2"""

    def __init__(self):
        self.embeddings = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id=bedrock_config.MODEL_ID,
            region_name=AWS_REGION,
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings com tratamento básico de erros"""
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logging.error(f"Falha na geração de embeddings: {str(e)}")
            raise

    def embed_documents(self, documents: List[Document]) -> List[Document]:
        """Processa documentos em lotes pequenos"""
        batch_size = 10  # Número conservador para evitar throttling
        embedded_docs = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            texts = [doc.page_content for doc in batch]

            try:
                embeddings = self.generate_embeddings(texts)
                for doc, emb in zip(batch, embeddings):
                    doc.metadata["embedding"] = emb
                    doc.metadata["embedding_status"] = "success"
                embedded_docs.extend(batch)

            except Exception:
                # Marca os falhados para reprocessamento
                for doc in batch:
                    doc.metadata["embedding_status"] = "failed"
                embedded_docs.extend(batch)

            time.sleep(0.2)  # Delay entre batches

        return embedded_docs


def initialize_embedding_service():
    return BedrockEmbeddingHandler()
