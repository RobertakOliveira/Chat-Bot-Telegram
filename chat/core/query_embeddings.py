# chat/core/query_embeddings.py
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, AWS_REGION
from chat.utils.config import bedrock_config
import re


def get_query_embedding(query: str) -> list[float]:
    """Gera embedding para perguntas com mesma limpeza dos textos jurídicos"""
    # Replica a limpeza do BedrockEmbeddingHandler
    query_limpa = re.sub(r'\x00', '', query).strip()[
        :bedrock_config.TEXT_TRUNCATE]

    model = BedrockEmbeddings(
        client=bedrock_runtime,
        model_id=bedrock_config.MODEL_ID,
        region_name=AWS_REGION
    )

    return model.embed_query(query_limpa)
