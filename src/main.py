import sys
import os

# 👉 Ajusta o PYTHONPATH antes de tudo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from flask import Flask
from controllers.main_controller import Main, ProcessQuery
from config import Config
from services.cloudwatch_logger_service import CloudWatchLoggerService

# Configurar o logger global com suporte a CloudWatch
logger = CloudWatchLoggerService.setup_logger(
    logger_name="chatbot_api",
    log_level=logging.INFO if not Config.DEBUG_MODE else logging.DEBUG,
    enable_cloudwatch=Config.ENABLE_CLOUDWATCH_LOGS,
    log_group=Config.CLOUDWATCH_LOG_GROUP
)

# Configurar loggers para todos os serviços
if Config.ENABLE_CLOUDWATCH_LOGS:
    logger.info("Configurando loggers de serviços para CloudWatch...")
    service_loggers = [
        'llm_service', 's3_service', 'config', 
        'retrieval_service', 'indexing_service',
        'bedrock_service', 'chroma_service', 'rag_service',
        'vector_search_service', 'embedding_service'
    ]
    
    # Obter cliente CloudWatch
    _, _, cloudwatch_client = Config.get_aws_clients()
    
    # Configurar cada logger de serviço
    for service_name in service_loggers:
        service_logger = logging.getLogger(service_name)
        CloudWatchLoggerService.add_cloudwatch_handler(
            existing_logger=service_logger,
            cloudwatch_client=cloudwatch_client,
            log_group_name=Config.CLOUDWATCH_LOG_GROUP
        )
    logger.info(f"✅ {len(service_loggers)} loggers de serviços configurados para CloudWatch")

app = Flask(__name__)

# Rota de saúde
@app.route("/", methods=["GET"])
def main():
    logger.info("Endpoint de saúde acessado")
    return Main()

# Rota de consulta RAG
@app.route("/query", methods=["POST"])
def process_query():
    logger.info("Requisição de consulta recebida")
    return ProcessQuery()

#teste local
#if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=5000, debug=True)
