# chat/core/bedrock_embeddings.py
import time
import logging
import hashlib
from typing import List, Dict, Any
from tenacity import retry, wait_exponential, stop_after_attempt
from langchain_core.documents import Document
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, AWS_REGION
from chat.utils.config import bedrock_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class BedrockEmbeddingHandler:
    """Gerador de embeddings otimizado para documentos jurídicos"""

    def __init__(self):
        self.embeddings = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id=bedrock_config.MODEL_ID,
            region_name=AWS_REGION
        )

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10),
           stop=stop_after_attempt(3))
    def _generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings com retentativas e logging detalhado"""
        start_time = time.time()
        try:
            embeddings = self.embeddings.embed_documents(texts)
            processing_time = (time.time() - start_time) * 1000

            logging.info(
                f"Embeddings gerados | "
                f"Textos: {len(texts)} | "
                f"Tempo: {processing_time:.2f}ms | "
                f"Dimensões: {len(embeddings[0]) if embeddings else 0}"
            )
            return embeddings

        except Exception as e:
            logging.error(f"Falha na geração de embeddings: {str(e)}")
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
            texts = [self._clean_text(doc.page_content) for doc in batch]

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
                logging.error(
                    f"Falha no lote {i//bedrock_config.BATCH_SIZE}: {str(e)}")
                # Registra falha sem interromper o fluxo
                results.extend([{
                    "id": "ERROR",
                    "text": doc.page_content,
                    "error": str(e)
                } for doc in batch])

            time.sleep(bedrock_config.BATCH_DELAY)

        return results

    def _clean_text(self, text: str) -> str:
        """Pré-processamento específico para textos jurídicos (mantido)"""
        return text.replace('\x00', '').strip()[:bedrock_config.TEXT_TRUNCATE]


def initialize_embedding_service():
    return BedrockEmbeddingHandler()
