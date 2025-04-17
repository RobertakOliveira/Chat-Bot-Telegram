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
            "EMBEDDING_DIMENSIONS": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/embedding-dimensions",
                    "EMBEDDING_DIMENSIONS",
                    "512"
                )),
            "BEDROCK_NORMALIZE_EMBEDDINGS": str(
                self._get_param_with_fallback(
                    "/chatbot-juridico/bedrock-normalize-embeddings",
                    "BEDROCK_NORMALIZE_EMBEDDINGS",
                    "True"
                )
            ).lower() in ("true", "1", "t"),  # Converte string para bool
            "MAX_TOKENS": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/max-tokens",
                    "MAX_TOKENS",
                    "8000"
                )),
            "BEDROCK_BATCH_SIZE": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/bedrock-batch-size",
                    "BEDROCK_BATCH_SIZE",
                    "48"
                )),
            "BEDROCK_MAX_RETRIES": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/bedrock-max-retries",
                    "BEDROCK_MAX_RETRIES",
                    "3"
                )),
            "BEDROCK_BATCH_DELAY": float(
                self._get_param_with_fallback(
                    "/chatbot-juridico/bedrock-batch-delay",
                    "BEDROCK_BATCH_DELAY",
                    "0.15"
                )),
            "BEDROCK_TEXT_TRUNCATE": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/bedrock-text-truncate",
                    "BEDROCK_TEXT_TRUNCATE",
                    "7500"  # Margem de segurança para tokenização
                )),

            # Configurações de PDF Processing
            "CHUNK_SIZE": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/chunk-size",
                    "CHUNK_SIZE",
                    "800"
                )),
            "CHUNK_OVERLAP": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/chunk-overlap",
                    "CHUNK_OVERLAP",
                    "150"
                )),
            "LEGAL_SEPARATORS": self._get_param_with_fallback(
                "/chatbot-juridico/legal-separators",
                "LEGAL_SEPARATORS",
                "\nArtigo ,\n§ ,\nParágrafo ,\nInciso ,\nAlínea ,\nCAPÍTULO ,\nSeção ,\n\n,\n, "
            )
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
    def CHUNK_SIZE(self) -> int:
        """int: Tamanho dos chunks de texto (em caracteres) para divisão do conteúdo PDF."""
        return config.CHUNK_SIZE

    @property
    def CHUNK_OVERLAP(self) -> int:
        """int: Número de caracteres de sobreposição entre chunks consecutivos."""
        return config.CHUNK_OVERLAP

    @property
    def LEGAL_SEPARATORS(self) -> list[str]:
        """
        list[str]: Separadores de texto válidos para divisão, com entradas vazias filtradas.

        Os separadores são obtidos dividindo e limpando uma string de configuração separada por vírgulas.
        """
        return [s.strip() for s in config.LEGAL_SEPARATORS.split(',') if s.strip()]

    @property
    def MIN_CHUNK_LENGTH(self) -> int:
        """int: Comprimento mínimo aceitável para chunks (20% do CHUNK_SIZE) para evitar fragmentos pequenos."""
        return int(config.CHUNK_SIZE * 0.2)  # 20% do chunk size

    @property
    def MAX_PAGE_LENGTH(self) -> int:
        """int: Número máximo de tokens por página, alinhado com o limite do modelo de linguagem."""
        return config.MAX_TOKENS  # Alinhado com limite do modelo

    ACCEPTED_MIME_TYPES = {
        'application/pdf',
        'application/x-pdf'
    }
    """set: Tipos MIME aceitos para arquivos PDF (tipos PDF e X-PDF)."""


class BedrockConfig:
    """Configurações especializadas para Bedrock"""

    @property
    def MODEL_ID(self) -> str:
        """str: ID do modelo fundacional da Bedrock a ser utilizado."""
        return config.BEDROCK_MODEL_ID

    @property
    def EMBEDDING_DIMENSIONS(self) -> int:
        """int: Dimensionalidade dos vetores de embeddings gerados."""
        return config.EMBEDDING_DIMENSIONS

    @property
    def NORMALIZE_EMBEDDINGS(self) -> bool:
        """bool: Indica se os embeddings devem ser normalizados (útil para operações de similaridade)."""
        return config.BEDROCK_NORMALIZE_EMBEDDINGS

    @property
    def MAX_TOKENS(self) -> int:
        """int: Número máximo de tokens permitidos por requisição, conforme limite do modelo."""
        return config.MAX_TOKENS

    @property
    def BATCH_SIZE(self) -> int:
        """int: Quantidade de requisições processadas por lote (melhora throughput)."""
        return config.BEDROCK_BATCH_SIZE

    @property
    def MAX_RETRIES(self) -> int:
        """int: Máximo de tentativas para requisições falhas (resiliência a erros transitórios)."""
        return config.BEDROCK_MAX_RETRIES

    @property
    def BATCH_DELAY(self) -> float:
        """float: Intervalo em segundos entre lotes de requisições (evita throttling da API)."""
        return config.BEDROCK_BATCH_DELAY

    @property
    def TEXT_TRUNCATE(self) -> str:
        """Define qual parte do texto será mantida quando exceder MAX_TOKENS."""
        return config.BEDROCK_TEXT_TRUNCATE


# 🔁 Singleton global
config = ConfigLoader()

# Instâncias especializadas
pdf_config = PDFConfig()
bedrock_config = BedrockConfig()

if __name__ == "__main__":
    # Teste de configuração
    print("\n===  🔒 Configurações Carregadas  🔒===")
    print("Infraestrutura:")
    print(f"- S3 Bucket: {config.S3_BUCKET_NAME}")
    print(f"- Log Group: {config.LOG_GROUP}")

    print("\nBedrock:")
    print(f"- Model ID: {bedrock_config.MODEL_ID}")
    print(f"- Embedding Dims: {bedrock_config.EMBEDDING_DIMENSIONS}")
    print(f"- Normalize: {bedrock_config.NORMALIZE_EMBEDDINGS}")
    print(f"- Max Tokens: {bedrock_config.MAX_TOKENS}")
    print(f"- Batch Size: {bedrock_config.BATCH_SIZE}")
    print(f"- Max Retries: {bedrock_config.MAX_RETRIES}")
    print(f"- Batch Delay: {bedrock_config.BATCH_DELAY}s")
    print(f"- Text Truncate: {bedrock_config.TEXT_TRUNCATE} chars")

    print("\nPDF Processing:")
    print(f"- Chunk Size: {pdf_config.CHUNK_SIZE}")
    print(f"- Chunk Overlap: {pdf_config.CHUNK_OVERLAP}")
    print(f"- Max Page Length: {pdf_config.MAX_PAGE_LENGTH}")
    print(f"- Legal Separators: {pdf_config.LEGAL_SEPARATORS}")
