# chat/utils/aws_clients.py
"""
Módulo centralizado para clientes AWS.

Fornece clientes configurados e prontos para uso em toda a aplicação.
Todas as configurações de região e retry são definidas aqui.
"""

import boto3
from botocore.config import Config
from typing import Optional

# Configuração global
AWS_REGION = "us-east-1"
BOTO3_CONFIG = Config(
    region_name=AWS_REGION,
    retries={
        "max_attempts": 3,
        "mode": "standard"
    }
)

# Inicialização condicional dos clientes (singleton pattern)
_clients = {}


def get_client(service_name: str, config: Optional[Config] = None) -> boto3.client:
    """
    Retorna um cliente AWS configurado, com reutilização de instâncias.

    Args:
        service_name: Nome do serviço AWS (ex: 's3', 'bedrock-runtime')
        config: Configuração customizada (opcional)

    Returns:
        Cliente boto3 configurado
    """
    if service_name not in _clients:
        _clients[service_name] = boto3.client(
            service_name,
            config=config or BOTO3_CONFIG
        )
    return _clients[service_name]


# Clientes pré-definidos para acesso rápido
bedrock_runtime = get_client("bedrock-runtime")
s3_client = get_client("s3")
logs_client = get_client("logs")
ssm_client = get_client("ssm")
sts_client = get_client("sts")
cloudwatch = get_client('cloudwatch')
