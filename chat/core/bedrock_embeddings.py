# chat/core/bedrock_embeddings.py
"""
Implementação do gerador de embeddings usando Bedrock.

Utiliza configurações centralizadas e clientes AWS compartilhados.
"""

from langchain_community.embeddings import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, logs_client
from chat.utils.config import config
import logging
import time

logger = logging.getLogger(__name__)


class BedrockEmbeddingGenerator:
    """
    Gera embeddings usando Amazon Bedrock com configuração centralizada.

    Attributes:
        embeddings: Instância do LangChain BedrockEmbeddings
    """

    def __init__(self, model_id: str = None):
        """
        Inicializa com modelo específico ou usa o padrão da configuração.

        Args:
            model_id: ID do modelo Bedrock (opcional)
        """
        self.embeddings = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id=model_id or config.BEDROCK_MODEL_ID
        )

    def generate_embedding(self, text: str) -> list:
        """
        Gera embedding para um texto e registra no CloudWatch.

        Args:
            text: Texto para gerar embedding

        Returns:
            Lista de floats representando o embedding

        Raises:
            Exception: Se falhar a geração do embedding
        """
        try:
            start_time = time.time()
            embedding = self.embeddings.embed_query(text)
            elapsed = (time.time() - start_time) * 1000

            self._log_to_cloudwatch(text, embedding, elapsed)
            logger.debug(f"Embedding gerado em {elapsed:.2f}ms")

            return embedding
        except Exception as e:
            logger.error(f"Falha ao gerar embedding: {str(e)}", exc_info=True)
            raise

    def _log_to_cloudwatch(self, text: str, embedding: list, elapsed_ms: float):
        """
        Registra métricas no CloudWatch.

        Args:
            text: Texto original
            embedding: Embedding gerado
            elapsed_ms: Tempo de processamento em milissegundos
        """
        try:
            logs_client.put_log_events(
                logGroupName=config.LOG_GROUP,
                logStreamName="embedding-generation",
                logEvents=[{
                    'timestamp': int(time.time() * 1000),
                    'message': (
                        f"Texto: {text[:100]}... | "
                        f"Dimensões: {len(embedding)} | "
                        f"Tempo: {elapsed_ms:.2f}ms"
                    )
                }]
            )
        except Exception as e:
            logger.warning(f"Falha ao registrar log: {str(e)}")
