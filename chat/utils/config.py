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
from botocore.exceptions import ClientError
from typing import Any, Dict
from chat.utils.aws_clients import ssm_client


class ConfigLoader:
    """
    Carrega configurações do SSM com fallback para variáveis de ambiente/defaults.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Carrega todas as configurações na inicialização"""
        self._config = {
            "S3_BUCKET_NAME": self._get_param("/chatbot-juridico/s3-bucket-name", "default-bucket"),
            "BEDROCK_MODEL_ID": self._get_param("/chatbot-juridico/bedrock-model-id", "amazon.titan-embed-text-v1"),
            "LOG_GROUP": self._get_param("/chatbot-juridico/log-group", "/aws/bedrock/embeddings")
        }

    def _get_param(self, name: str, default: Any) -> Any:
        """
        Tenta obter parâmetro do SSM, fallback para env var/default.

        Args:
            name: Nome do parâmetro no SSM
            default: Valor padrão se não encontrado

        Returns:
            Valor do parâmetro ou default
        """
        try:
            response = ssm_client.get_parameter(Name=name, WithDecryption=True)
            return response['Parameter']['Value']
        except ClientError as e:
            print(
                f"[CONFIG] Parâmetro {name} não encontrado, usando fallback. Erro: {e}")
            return os.getenv(name.replace('/', '_').upper(), default)

    def __getattr__(self, name: str) -> Any:
        """Acesso às configurações como propriedades"""
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"Configuração {name} não encontrada")


# Singleton acessível globalmente
config = ConfigLoader()
if __name__ == "__main__":
    # Teste de carga das configurações
    print(f"Bucket S3: {S3_BUCKET_NAME}")
    print(f"Modelo Bedrock: {BEDROCK_MODEL_ID}")
