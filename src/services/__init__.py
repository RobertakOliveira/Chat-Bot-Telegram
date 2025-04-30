# Módulo de serviços
import logging
from config import Config

# Configuração global de logging para serviços
logging.basicConfig(
    level=logging.INFO if not Config.DEBUG_MODE else logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Função para configurar logger de serviço
def setup_service_logger(service_name):
    """
    Configura um logger para um serviço específico 
    
    Args:
        service_name: Nome do serviço/módulo
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(service_name)
    
    # Já define o nível de log baseado na configuração global
    logger.setLevel(logging.INFO if not Config.DEBUG_MODE else logging.DEBUG)
    
    return logger

# Exporta serviços principais
from .s3_service import S3Service
from .llm_service import LLMService
from .cloudwatch_logger_service import CloudWatchLoggerService
