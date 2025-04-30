import os
import boto3
import logging
from dotenv import load_dotenv

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("config")

# Carrega as variáveis de ambiente do arquivo .env
# load_dotenv(override=True)

class Config:
    # Configurações S3
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    
    # Configurações Bedrock
    BEDROCK_REGION = os.environ.get('BEDROCK_REGION', 'us-east-1')
    EMBEDDING_MODEL_ID = os.environ.get('BEDROCK_EMBEDDING_MODEL', 'amazon.titan-embed-text-v2:0')
    
    # Configurações ChromaDB
    CHROMA_COLLECTION = os.environ.get('CHROMA_COLLECTION', 'documentos_processados')
    CHROMA_BASE_DIR = os.environ.get('CHROMA_BASE_DIR', 'bd')
    CHROMA_DB_NAME = os.environ.get('CHROMA_DB_NAME', 'chroma_db')
    CHROMA_LOCAL_PATH = os.path.join(CHROMA_BASE_DIR, CHROMA_DB_NAME)
    
    # Configurações de processamento
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '100'))
    MAX_CONTEXT_DOCS = int(os.environ.get('MAX_CONTEXT_DOCS', '5'))
    
    # AWS
    AWS_PROFILE = os.environ.get('AWS_PROFILE', None)
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'True').lower() == 'true'
    
    # CloudWatch Logs
    CLOUDWATCH_LOG_GROUP = os.environ.get('CLOUDWATCH_LOG_GROUP', 'juridico-rag-app')
    CLOUDWATCH_REGION = os.environ.get('CLOUDWATCH_REGION', BEDROCK_REGION)
    ENABLE_CLOUDWATCH_LOGS = os.environ.get('ENABLE_CLOUDWATCH_LOGS', 'true').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """
        Valida as configurações obrigatórias
        """
        if not cls.S3_BUCKET_NAME:
            raise ValueError("A variável de ambiente S3_BUCKET_NAME é obrigatória")
        
        # Garante que os diretórios para o ChromaDB existam
        os.makedirs(cls.CHROMA_BASE_DIR, exist_ok=True)
        
        logger.info(f"Diretório ChromaDB configurado: {cls.CHROMA_LOCAL_PATH}")
        logger.info("Configurações validadas com sucesso")
    
    @classmethod
    def get_aws_session(cls):
        """
        Cria uma sessão AWS usando perfil se disponível, senão usa credenciais padrão
        """

        try:
            if cls.AWS_PROFILE and len(cls.AWS_PROFILE) != 0:
                logger.info(f"Usando perfil AWS: {cls.AWS_PROFILE}")
                return boto3.Session(profile_name=cls.AWS_PROFILE)
            else:
                logger.info("Usando credenciais padrão AWS")
                return boto3.Session()
        except Exception as e:
            logger.error(f"Erro ao criar sessão AWS: {str(e)}")
            raise
    
    @classmethod
    def get_aws_clients(cls):
        """
        Cria e retorna os clientes AWS necessários
        """
        session = cls.get_aws_session()
        
        s3_client = session.client('s3')
        bedrock_client = session.client(
            service_name='bedrock-runtime',
            region_name=cls.BEDROCK_REGION
        )
        
        cloudwatch_client = None
        if cls.ENABLE_CLOUDWATCH_LOGS:
            cloudwatch_client = session.client(
                service_name='logs',
                region_name=cls.CLOUDWATCH_REGION
            )
            logger.info(f"Cliente CloudWatch Logs criado (região: {cls.CLOUDWATCH_REGION})")
        
        logger.info(f"Clientes AWS criados (região Bedrock: {cls.BEDROCK_REGION})")
        
        return s3_client, bedrock_client, cloudwatch_client 