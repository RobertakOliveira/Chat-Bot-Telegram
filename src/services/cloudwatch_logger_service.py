import os
import logging
import watchtower
import datetime
from config import Config

class CloudWatchLoggerService:
    """
    Serviço para configurar logging no AWS CloudWatch
    """
    
    @classmethod
    def setup_logger(cls, 
                     logger_name="app", 
                     log_level=logging.INFO, 
                     enable_cloudwatch=False, 
                     log_group=None,
                     log_stream_prefix=None):
        """
        Configura um logger com suporte a CloudWatch
        
        Args:
            logger_name: Nome do logger
            log_level: Nível de logging
            enable_cloudwatch: Se True, habilita o envio de logs para CloudWatch
            log_group: Nome do grupo de logs no CloudWatch
            log_stream_prefix: Prefixo para o stream de logs
            
        Returns:
            logging.Logger: O logger configurado
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        
        # Limpa handlers existentes para evitar duplicação
        if logger.handlers:
            logger.handlers.clear()
        
        # Adiciona um handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # Se CloudWatch estiver habilitado e tivermos um cliente disponível
        if enable_cloudwatch:
            try:
                _, _, cloudwatch_client = Config.get_aws_clients()
                
                if cloudwatch_client:
                    # Configura nome do grupo e stream
                    log_group_name = log_group or Config.CLOUDWATCH_LOG_GROUP
                    stream_prefix = log_stream_prefix or datetime.datetime.now().strftime('%Y-%m-%d')
                    log_stream_name = f"{stream_prefix}-{os.environ.get('ENVIRONMENT', 'dev')}"
                    
                    # Cria handler do watchtower
                    cw_handler = watchtower.CloudWatchLogHandler(
                        log_group_name=log_group_name,
                        log_stream_name=log_stream_name,
                        boto3_client=cloudwatch_client
                    )
                    cw_handler.setLevel(log_level)
                    cw_handler.setFormatter(console_format)
                    
                    # Adiciona o handler ao logger
                    logger.addHandler(cw_handler)
                    logger.info(f"CloudWatch logging habilitado: grupo={log_group_name}, stream={log_stream_name}")
                else:
                    logger.warning("Cliente CloudWatch não disponível. O logging no CloudWatch não será habilitado.")
            except Exception as e:
                logger.error(f"Erro ao configurar CloudWatch logging: {str(e)}")
                logger.warning("Continuando sem logging no CloudWatch")
        else:
            logger.info("CloudWatch logging desabilitado por configuração")
        
        return logger
    
    @classmethod
    def add_cloudwatch_handler(cls, existing_logger, cloudwatch_client, log_group_name, log_stream_prefix=None):
        """
        Adiciona um handler de CloudWatch a um logger existente
        
        Args:
            existing_logger: Logger existente para adicionar o handler
            cloudwatch_client: Cliente boto3 para CloudWatch Logs
            log_group_name: Nome do grupo de logs
            log_stream_prefix: Prefixo para o stream de logs (default: data atual)
            
        Returns:
            logging.Logger: O logger atualizado
        """
        if not cloudwatch_client:
            existing_logger.warning("Cliente CloudWatch não fornecido. O logging no CloudWatch não será habilitado.")
            return existing_logger
        
        try:
            # Configura nome do stream
            stream_prefix = log_stream_prefix or datetime.datetime.now().strftime('%Y-%m-%d')
            log_stream_name = f"{stream_prefix}-{os.environ.get('ENVIRONMENT', 'dev')}"
            
            # Cria handler do watchtower
            cw_handler = watchtower.CloudWatchLogHandler(
                log_group_name=log_group_name,
                log_stream_name=log_stream_name,
                boto3_client=cloudwatch_client
            )
            
            # Define o formato dos logs
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )
            cw_handler.setFormatter(formatter)
            
            # Adiciona o handler ao logger
            existing_logger.addHandler(cw_handler)
            existing_logger.info(f"CloudWatch handler adicionado: grupo={log_group_name}, stream={log_stream_name}")
            
            return existing_logger
        except Exception as e:
            existing_logger.error(f"Erro ao adicionar handler CloudWatch: {str(e)}")
            return existing_logger 