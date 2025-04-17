# chat/core/bedrock_embeddings.py
import time
import hashlib
from typing import List, Dict, Any
from tenacity import retry, wait_exponential, stop_after_attempt
from langchain_core.documents import Document
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, AWS_REGION
from chat.utils.config import bedrock_config
from chat.utils.logger import logger
from chat.utils.clean_text import clean_text


class BedrockEmbeddingHandler:
    """Gerador de embeddings otimizado para documentos jurídicos"""

    def __init__(self):
        self.embeddings = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id=bedrock_config.MODEL_ID,
            region_name=AWS_REGION
        )
        logger.info(
            f"Inicializado BedrockEmbeddings com {bedrock_config.MODEL_ID}")

    @retry(
        wait=wait_exponential(
            multiplier=bedrock_config.RETRY_MULTIPLIER,
            min=bedrock_config.MIN_RETRY_DELAY,
            max=bedrock_config.MAX_RETRY_DELAY
        ),
        stop=stop_after_attempt(bedrock_config.MAX_RETRIES)
    )
    def _generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings com retentativas e logger detalhado"""
        start_time = time.time()
        try:
            embeddings = self.embeddings.embed_documents(texts)
            processing_time = (time.time() - start_time) * 1000

            logger.info(
                f"Embeddings gerados | "
                f"Textos: {len(texts)} | "
                f"Tempo: {processing_time:.2f}ms | "
                f"Dimensões: {len(embeddings[0]) if embeddings else 0}"
            )
            return embeddings

        except Exception as e:
            logger.error(f"Falha na geração de embeddings: {str(e)}")
            raise

    def _generate_doc_id(self, text: str) -> str:
        """Gera ID único para controle de versão"""
        return hashlib.sha256(text.encode()).hexdigest()[:12]

    def process_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Nova saída formatada para integração:
        Retorna lista de dicionários com estrutura padronizada
        """
        results = []

        for i in range(0, len(documents), bedrock_config.BATCH_SIZE):
            batch = documents[i:i + bedrock_config.BATCH_SIZE]
            texts = [clean_text(doc.page_content) for doc in batch]

            try:
                embeddings = self._generate_batch(texts)

                for doc, emb in zip(batch, embeddings):
                    results.append({
                        "id": self._generate_doc_id(doc.page_content),
                        "text": doc.page_content,
                        "embedding": emb,
                        "metadata": doc.metadata
                    })

            except Exception as e:
                logger.error(
                    f"Falha no lote {i//bedrock_config.BATCH_SIZE}: {str(e)}")
                # Registra falha sem interromper o fluxo
                results.extend([{
                    "id": "ERROR",
                    "text": doc.page_content,
                    "error": str(e)
                } for doc in batch])

            time.sleep(bedrock_config.BATCH_DELAY)

        return results


def initialize_embedding_service():
    return BedrockEmbeddingHandler()
