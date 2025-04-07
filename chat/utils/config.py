# chat/utils/config.py
"""
Configurações centralizadas para o Chatbot Jurídico.

Este módulo lê parâmetros de infraestrutura (S3, Bedrock) do AWS SSM Parameter Store,
evitando hardcodes no código. As variáveis são carregadas durante a inicialização.

Dependências:
- Terraform: Deve criar os parâmetros no SSM (ex: /chatbot-juridico/s3-bucket-name).
- IAM: A instância/role do chatbot precisa de permissões para ssm:GetParameter.
"""

import os
from typing import Any
from botocore.exceptions import ClientError
from chat.utils.aws_clients import ssm_client


class ConfigLoader:
    """Carrega configurações do SSM com fallbacks inteligentes."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Carrega todas as configurações com valores padrão otimizados"""
        self._config = {
            # Configurações existentes
            "S3_BUCKET_NAME": self._get_param("/chatbot-juridico/s3-bucket-name", "consultor-juridico"),
            "BEDROCK_MODEL_ID": self._get_param("/chatbot-juridico/bedrock-model-id", "amazon.titan-embed-text-v2:0"),
            "LOG_GROUP": self._get_param("/chatbot-juridico/log-group", "/aws/legal-bot/embeddings"),

            # Novas configurações (adicionadas)
            "EMBEDDING_DIMENSIONS": int(self._get_param("/chatbot-juridico/embedding-dimensions", "512")),
            "CHUNK_SIZE": int(self._get_param("/chatbot-juridico/chunk-size", "800")),
            "CHUNK_OVERLAP": int(self._get_param("/chatbot-juridico/chunk-overlap", "150")),
            "MAX_TOKENS": int(self._get_param("/chatbot-juridico/max-tokens", "8000"))
        }

    def _get_param(self, name: str, default: Any) -> Any:
        """Obtém parâmetro com tratamento de erros robusto."""
        try:
            response = ssm_client.get_parameter(Name=name, WithDecryption=True)
            return response['Parameter']['Value']
        except ClientError as e:
            env_var = name.replace('/', '_').upper()
            print(
                f"[CONFIG] Parâmetro {name} não encontrado, usando {env_var} ou default. Erro: {e}")
            return os.getenv(env_var, default)

    def __getattr__(self, name: str) -> Any:
        """Acesso type-safe às configurações."""
        if name in self._config:
            return self._config[name]
        raise AttributeError(
            f"Configuração {name} não existe. Opções válidas: {list(self._config.keys())}")


# 🔁 Singleton global
config = ConfigLoader()

if __name__ == "__main__":
    # Teste de configuração
    print("\nConfigurações Carregadas:")
    print(f"- Bucket S3: {config.S3_BUCKET_NAME}")
    print(f"- Modelo Bedrock: {config.BEDROCK_MODEL_ID}")
    print(f"- Dimensões: {config.EMBEDDING_DIMENSIONS}")
    print(f"- Tamanho do Chunk: {config.CHUNK_SIZE} caracteres")
    print(f"- Sobreposição: {config.CHUNK_OVERLAP} caracteres")
