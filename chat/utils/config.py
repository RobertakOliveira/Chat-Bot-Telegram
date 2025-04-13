# chat/utils/config.py
"""
Configurações centralizadas para o Chatbot Jurídico.
    Padrão de vars para produção em alguns pontos _ à ser definido _

Funcionamento híbrido:
1. Tenta carregar do AWS SSM Parameter Store
2. Fallback para variáveis de ambiente
3. Fallback para valores padrão otimizados

Dependências:
- AWS: Configurações no SSM (/chatbot-juridico/*)
- Local: Variáveis de ambiente ou valores padrão

Prioridade de carregamento:
SSM > Env Vars > Default Values
"""

import os
from typing import Any
from botocore.exceptions import ClientError, NoCredentialsError

try:
    from chat.utils.aws_clients import ssm_client
    AWS_AVAILABLE = True
except (ImportError, NoCredentialsError):
    AWS_AVAILABLE = False


class ConfigLoader:
    """Carrega configurações do SSM com fallbacks inteligentes (Singleton)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Carrega todas as configurações com hierarquia de fallback"""
        self._config = {
            # Configurações de Infraestrutura AWS
            "S3_BUCKET_NAME": self._get_param_with_fallback(
                "/chatbot-juridico/s3-bucket-name",
                "S3_BUCKET_NAME",
                "consultor-juridico"
            ),
            "LOG_GROUP": self._get_param_with_fallback(
                "/chatbot-juridico/log-group",
                "LOG_GROUP",
                "/aws/legal-bot/embeddings"
            ),

            # Configurações do Bedrock
            "BEDROCK_MODEL_ID": self._get_param_with_fallback(
                "/chatbot-juridico/bedrock-model-id",
                "BEDROCK_MODEL_ID",
                "amazon.titan-embed-text-v2:0"
            ),
            "EMBEDDING_DIMENSIONS": int(self._get_param_with_fallback(
                "/chatbot-juridico/embedding-dimensions",
                "EMBEDDING_DIMENSIONS",
                "512"
            )),
            "MAX_TOKENS": int(self._get_param_with_fallback(
                "/chatbot-juridico/max-tokens",
                "MAX_TOKENS",
                "8000"
            )),

            # Configurações de PDF Processing
            "CHUNK_SIZE": int(self._get_param_with_fallback(
                "/chatbot-juridico/chunk-size",
                "CHUNK_SIZE",
                "800"
            )),
            "CHUNK_OVERLAP": int(self._get_param_with_fallback(
                "/chatbot-juridico/chunk-overlap",
                "CHUNK_OVERLAP",
                "150"
            ))
        }

    def _get_param_with_fallback(self, ssm_name: str, env_var: str, default: Any) -> Any:
        """Hierarquia de resolução: SSM > Env Var > Default"""
        # 1. Tentar SSM se disponível
        if AWS_AVAILABLE:
            try:
                response = ssm_client.get_parameter(
                    Name=ssm_name, WithDecryption=True)
                return response['Parameter']['Value']
            except ClientError:
                pass

            # 2. Tentar Env Var
            env_value = os.getenv(env_var)
            if env_value is not None:
                return env_value

            # 3. Usar default
            print(
                f"[CONFIG] Usando valor padrão para {env_var} (SSM não encontrado)")
            return default

    def __getattr__(self, name: str) -> Any:
        """Acesso type-safe às configurações."""
        if name in self._config:
            return self._config[name]
        raise AttributeError(
            f"Configuração {name} não existe. Opções válidas: {list(self._config.keys())}")


class PDFConfig:
    """Configurações especializadas para processamento de PDF"""

    @property
    def CHUNK_SIZE(self):
        return config.CHUNK_SIZE

    @property
    def CHUNK_OVERLAP(self):
        return config.CHUNK_OVERLAP

    # Constantes específicas de PDF
    MIN_CHUNK_LENGTH = 50
    MAX_PAGE_LENGTH = 10000  # Prevenção contra PDFs corrompidos
    ACCEPTED_MIME_TYPES = {
        'application/pdf',
        'application/x-pdf'
    }


class BedrockConfig:
    """Configurações especializadas para Bedrock"""

    @property
    def MODEL_ID(self):
        return config.BEDROCK_MODEL_ID

    @property
    def EMBEDDING_DIMENSIONS(self):
        return config.EMBEDDING_DIMENSIONS

    @property
    def MAX_TOKENS(self):
        return config.MAX_TOKENS


# 🔁 Singleton global
config = ConfigLoader()

# Instâncias especializadas
pdf_config = PDFConfig()
bedrock_config = BedrockConfig()

if __name__ == "__main__":
    # Teste de configuração
    print("\n=== Configurações Carregadas ===")
    print("Infraestrutura:")
    print(f"- S3 Bucket: {config.S3_BUCKET_NAME}")
    print(f"- Log Group: {config.LOG_GROUP}")

    print("\nBedrock:")
    print(f"- Model ID: {bedrock_config.MODEL_ID}")
    print(f"- Embedding Dims: {bedrock_config.EMBEDDING_DIMENSIONS}")
    print(f"- Max Tokens: {bedrock_config.MAX_TOKENS}")

    print("\nPDF Processing:")
    print(f"- Chunk Size: {pdf_config.CHUNK_SIZE}")
    print(f"- Chunk Overlap: {pdf_config.CHUNK_OVERLAP}")
    print(f"- Max Page Length: {pdf_config.MAX_PAGE_LENGTH}")
