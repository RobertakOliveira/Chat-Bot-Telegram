# chat/core/bedrock_embeddings.py
"""
Implementação do gerador de embeddings usando Bedrock.

Utiliza configurações centralizadas e clientes AWS compartilhados.
"""
import json
import time
import logging
from typing import Dict, Any
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, logs_client, s3_client
from chat.utils.config import config


class BedrockEmbeddingHandler:
    """Manipulador de embeddings com Bedrock com logging completo"""

    def __init__(self):
        self.embeddings = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id=config.BEDROCK_MODEL_ID
        )
        self._setup_logging()

    def _setup_logging(self):
        """Configura streams de log no CloudWatch"""
        try:
            logs_client.create_log_group(logGroupName=config.LOG_GROUP)
        except logs_client.exceptions.ResourceAlreadyExistsException:
            pass

        try:
            logs_client.create_log_stream(
                logGroupName=config.LOG_GROUP,
                logStreamName="embedding-service"
            )
        except logs_client.exceptions.ResourceAlreadyExistsException:
            pass

    def _log_embedding_operation(self, operation_data: Dict[str, Any]):
        """Registra operações no CloudWatch"""
        log_entry = {
            "timestamp": int(time.time() * 1000),
            "operation": "generate_embedding",
            "data": {
                "document_source": operation_data.get("source"),
                "text_length": len(operation_data["text"]),
                "processing_time_ms": operation_data["processing_time"],
                "embedding_dimensions": len(operation_data["embedding"]),
                "s3_destination": operation_data["s3_path"]
            }
        }

        try:
            logs_client.put_log_events(
                logGroupName=config.LOG_GROUP,
                logStreamName="embedding-service",
                logEvents=[{"timestamp": log_entry["timestamp"],
                            "message": json.dumps(log_entry)}]
            )
        except Exception as e:
            logging.error(f"Falha no log: {str(e)}")

    def generate_embedding(self, text: str, s3_bucket_name: str, final_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Gera e armazena embedding com metadados completos"""
        start_time = time.time()

        try:
            embedding = self.embeddings.embed_query(text)
            processing_time = (time.time() - start_time) * 1000

            document_data = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata,
                "version": "1.0",
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

            s3_client.put_object(
                Bucket=s3_bucket_name,
                Key=final_path,
                Body=json.dumps(document_data, ensure_ascii=False),
                Metadata={
                    "document-type": metadata.get("doc_type", "unknown"),
                    "page-number": str(metadata.get("page_number", 0))
                }
            )

            self._log_embedding_operation({
                "text": text,
                "embedding": embedding,
                "processing_time": processing_time,
                "s3_path": final_path,
                "source": metadata.get("source")
            })

            return {
                "status": "success",
                "s3_location": f"s3://{s3_bucket_name}/{final_path}",
                "embedding_dimensions": len(embedding)
            }

        except Exception as e:
            logging.error(f"Falha na geração de embedding: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }


def initialize_embedding_service():
    """Inicializa o serviço de embeddings"""
    return BedrockEmbeddingHandler()
