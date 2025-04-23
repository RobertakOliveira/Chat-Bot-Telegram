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
import re
from typing import Any
from botocore.exceptions import ClientError, NoCredentialsError
from chat.utils.logger import get_logger

logger = get_logger("config")

try:
    from chat.utils.aws_clients import ssm_client
    AWS_AVAILABLE = True
except (ImportError, NoCredentialsError):
    AWS_AVAILABLE = False


class ConfigLoader:
    """Carrega configurações do SSM com fallbacks inteligentes (Singleton)."""

    _instance = None
    _cache = {}

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
                "/aws/chatbot-consultor-juridico"
            ),

            # Configurações do Bedrock
            "BEDROCK_MODEL_ID": self._get_param_with_fallback(
                "/chatbot-juridico/bedrock-model-id",
                "BEDROCK_MODEL_ID",
                "amazon.titan-embed-text-v2:0"
            ),
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
            "BEDROCK_RETRY_MULTIPLIER": float(
                self._get_param_with_fallback(
                    "/chatbot-juridico/bedrock-retry-multiplier",
                    "BEDROCK_RETRY_MULTIPLIER",
                    "1"
                )),
            "BEDROCK_MIN_RETRY_DELAY": float(
                self._get_param_with_fallback(
                    "/chatbot-juridico/bedrock-min-retry-delay",
                    "BEDROCK_MIN_RETRY_DELAY",
                    "2"
                )),
            "BEDROCK_MAX_RETRY_DELAY": float(
                self._get_param_with_fallback(
                    "/chatbot-juridico/bedrock-max-retry-delay",
                    "BEDROCK_MAX_RETRY_DELAY",
                    "10"
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
                    "1200"
                )),
            "CHUNK_OVERLAP": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/chunk-overlap",
                    "CHUNK_OVERLAP",
                    "300"
                )),
            "MAX_TOKENS": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/max-tokens",
                    "MAX_TOKENS",
                    "8000"
                )),
            "PDF_PREFIX": self._get_param_with_fallback(
                "/chatbot-juridico/pdf-prefix",
                "PDF_PREFIX",
                "juridicos/"
            ),
            "LEGAL_SEPARATORS": self._get_param_with_fallback(
                "/chatbot-juridico/legal-separators",
                "LEGAL_SEPARATORS",
                "\nArtigo,\n§,\nParágrafo,\nInciso,\nAlínea,\nCAPÍTULO,\nSeção,\n\n,\n, "
            ),
            "LEGAL_IGNORE_PATTERNS": self._get_param_with_fallback(
                "/chatbot-juridico/legal-ignore-patterns",
                "LEGAL_IGNORE_PATTERNS",
                r"Documento assinado digitalmente,"
                r"Fl\. \d+,"
                r"Página \d+,"
                r"Processo: \d+-\d+\.\d+\.\d+\.\d+\.\d+,"
                r"https?://[^\s]+,"
                r"Assinado\s(eletronicamente|digitalmente)\spor:.*?\d{2}/\d{2}/\d{4},"
                r"N(ú|u)mero\sdo\sdocumento:.*?\d+,"
                r"\(e-STJ\sFl\.\d+\),"
                r"Num\.\s\d+\s-\sPág\.\s\d+,"
                r"S\sE\sL\sA\sJ\sA\sZ\sU\sO\sS\sN\sR\sÁ\sK.*?(?=\n|$),"
                r"i+f+i+.*?m+\d+,"
                r"^\s*[\W\d]{1,3}\s*$"
            ),
            "LEGAL_PRESERVE_PATTERNS": self._get_param_with_fallback(
                "/chatbot-juridico/legal-preserve-patterns",
                "LEGAL_PRESERVE_PATTERNS",
                r"Art\. \d+º.*?(?=\nArt\.|\n§|$),§ \d+º.*?(?=\n§|\nArt\.|$),VOTO:.*?(?=ACÓRDÃO:|$),RELATÓRIO:.*?(?=VOTO:|$),ACÓRDÃO:.*?(?=PROCESSO:|$)"
            ),
            "MIN_VALID_CHUNK_LINES": int(
                self._get_param_with_fallback(
                    "/chatbot-juridico/min-valid-chunk-lines",
                    "MIN_VALID_CHUNK_LINES",
                    "3"
                ))
        }

    def _get_param_with_fallback(self, ssm_name: str, env_var: str, default: Any) -> Any:
        """Hierarquia de resolução: SSM > Env Var > Default"""

        # Checa se o valor já está no cache
        if ssm_name in self._cache:
            return self._cache[ssm_name]

        # 1. Tentar SSM se disponível
        if AWS_AVAILABLE:
            try:
                response = ssm_client.get_parameter(
                    Name=ssm_name, WithDecryption=True)
                value = response['Parameter']['Value']
                # Armazena no cache
                self._cache[ssm_name] = value
                return value
            except ClientError:
                pass

        # 2. Tentar Env Var
        env_value = os.getenv(env_var)
        if env_value is not None:
            self._cache[ssm_name] = env_value  # Armazena no cache
            return env_value

        # 3. Usar default
        logger.info(
            f"[CONFIG] Usando default para {env_var} (SSM não encontrado)")
        self._cache[ssm_name] = default  # Armazena no cache
        return default

    def __getattr__(self, name: str) -> Any:
        """Acesso type-safe às configurações."""
        if name in self._config:
            return self._config[name]
        raise AttributeError(
            f"Configuração {name} não existe. Opções válidas: {list(self._config.keys())}")


class PDFConfig:
    """Configurações especializadas para processamento de PDF"""

    def __init__(self):
        # Cache interno para padrões compilados
        self._compiled_ignore = None
        self._compiled_preserve = None

    @property
    def LEGAL_IGNORE_PATTERNS(self) -> list[re.Pattern]:
        """Padrões compilados (cacheados na primeira chamada)"""
        if self._compiled_ignore is None:
            patterns = [p.strip()
                        for p in config.LEGAL_IGNORE_PATTERNS.split(',') if p.strip()]
            self._compiled_ignore = [re.compile(
                p, re.IGNORECASE) for p in patterns]
        return self._compiled_ignore

    @property
    def LEGAL_PRESERVE_PATTERNS(self) -> list[re.Pattern]:
        """Padrões compilados (cacheados na primeira chamada)"""
        if self._compiled_preserve is None:
            patterns = [
                p.strip() for p in config.LEGAL_PRESERVE_PATTERNS.split(',') if p.strip()]
            self._compiled_preserve = [re.compile(p) for p in patterns]
        return self._compiled_preserve

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

    @property
    def PDF_PREFIX(self) -> str:
        """str: Prefixo do caminho S3 para arquivos PDF."""
        return config.PDF_PREFIX

    @property
    def ACCEPTED_MIME_TYPES(self) -> set:
        """Tipos MIME aceitos para upload"""
        return {'application/pdf', 'application/x-pdf'}

    @property
    def MIN_VALID_CHUNK_LINES(self) -> int:
        """Número mínimo de linhas válidas"""
        return config.MIN_VALID_CHUNK_LINES


class BedrockConfig:
    """Configurações especializadas para Bedrock"""

    @property
    def MODEL_ID(self) -> str:
        """str: ID do modelo fundacional da Bedrock a ser utilizado."""
        return config.BEDROCK_MODEL_ID

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
    def RETRY_MULTIPLIER(self) -> float:
        return config.BEDROCK_RETRY_MULTIPLIER

    @property
    def MIN_RETRY_DELAY(self) -> float:
        return config.BEDROCK_MIN_RETRY_DELAY

    @property
    def MAX_RETRY_DELAY(self) -> float:
        return config.BEDROCK_MAX_RETRY_DELAY

    @property
    def BATCH_DELAY(self) -> float:
        """float: Intervalo em segundos entre lotes de requisições (evita throttling da API)."""
        return config.BEDROCK_BATCH_DELAY

    @property
    def TEXT_TRUNCATE(self) -> int:
        """Define qual parte do texto será mantida quando exceder MAX_TOKENS."""
        return config.BEDROCK_TEXT_TRUNCATE


# 🔁 Singleton global
config = ConfigLoader()

# Instâncias especializadas
pdf_config = PDFConfig()
bedrock_config = BedrockConfig()

if __name__ == "__main__":
    # Teste de configuração
    logger.info("\n===  🔒 Configurações Carregadas  🔒 ===")
    logger.info("\n=== 🌐 Infraestrutura === ")
    logger.info(f"- S3 Bucket: {config.S3_BUCKET_NAME}")
    logger.info(f"- Log Group: {config.LOG_GROUP}")

    logger.info("\n=== 🪨  Bedrock === ")
    logger.info(f"- Model ID: {bedrock_config.MODEL_ID}")
    logger.info(f"- Batch Size: {bedrock_config.BATCH_SIZE}")
    logger.info(f"- Max Retries: {bedrock_config.MAX_RETRIES}")
    logger.info(f"- Batch Delay: {bedrock_config.BATCH_DELAY}s")
    logger.info(f"- Text Truncate: {bedrock_config.TEXT_TRUNCATE} chars")

    logger.info("\n=== ⚖️  Padrões Jurídicos Carregados === ")
    logger.info(f"- Chunk Size: {pdf_config.CHUNK_SIZE}")
    logger.info(f"- Chunk Overlap: {pdf_config.CHUNK_OVERLAP}")
    logger.info(f"- Max Page Length: {pdf_config.MAX_PAGE_LENGTH}")
    logger.info(f"- Legal Separators: {pdf_config.LEGAL_SEPARATORS}")
    logger.info(
        f"- Ignorar: {[p.pattern for p in pdf_config.LEGAL_IGNORE_PATTERNS]}"
    )
    logger.info(
        f"- Preservar: {[p.pattern for p in pdf_config.LEGAL_PRESERVE_PATTERNS]}"
    )
    logger.info(
        f"- Linhas mínimas: {pdf_config.MIN_VALID_CHUNK_LINES}"
    )
