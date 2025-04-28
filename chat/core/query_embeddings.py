# chat/core/query_embeddings.py
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, AWS_REGION
from chat.utils.config import bedrock_config
# Importa a função de limpeza de texto
from chat.utils.clean_text import clean_text


class BedrockEmbeddingSingleton:
    """Classe Singleton para garantir que apenas uma instância do modelo BedrockEmbeddings seja criada"""
    _instance = None

    @classmethod
    def get_instance(cls):
        """Retorna a instância única do modelo BedrockEmbeddings.

        A instância do modelo será criada apenas na primeira chamada e reutilizada nas próximas.
        """
        if cls._instance is None:
            cls._instance = BedrockEmbeddings(
                client=bedrock_runtime,
                model_id=bedrock_config.BEDROCK_EMBEDDING_MODEL_ID,
                region_name=AWS_REGION
            )
        return cls._instance


def get_query_embedding(query: str) -> list[float]:
    """Gera o embedding para uma consulta do usuário (pergunta).

    Limpa a consulta (texto da pergunta), cria um embedding usando o modelo Bedrock
    e retorna uma lista de floats que representa o embedding da consulta.

    Parâmetros:
    query (str): A pergunta do usuário enviada pelo chatbot (via Telegram).

    Retorna:
    list[float]: O embedding gerado para a pergunta, que pode ser usado para busca ou geração de resposta.
    """
    # Limpeza da consulta, removendo caracteres indesejados e truncando o tamanho
    # Função que limpa o texto, como no exemplo de documentos jurídicos
    query_limpa = clean_text(query)

    # Obtém a instância única do modelo BedrockEmbeddings
    model = BedrockEmbeddingSingleton.get_instance()

    # Gera o embedding da consulta (pergunta)
    embedding = model.embed_query(query_limpa)

    return embedding

# Navegue até a pasta raiz e execute:
#     python -m chat.core.query_embeddings


# Função que recebe a mensagem do usuário e gera uma resposta usando RAG.
# TODO: Esta função precisa chamar a função `get_query_embedding` para gerar o embedding da
# consulta (pergunta) do usuário. Em seguida, o embedding gerado será utilizado para recuperar
# documentos ou gerar uma resposta.


# Processa a consulta do usuário no RAG (Recuperação com Geração).
# TODO: A função deve usar o embedding gerado pela consulta do usuário para buscar documentos
# relevantes. Em seguida, esses documentos devem ser usados para gerar uma resposta final.
