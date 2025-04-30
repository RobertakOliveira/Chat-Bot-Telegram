import time
import logging
import uuid
import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from langchain_core.callbacks import CallbackManager, StdOutCallbackHandler
from langchain_core.tracers import ConsoleCallbackHandler

from src.config import Config
from src.services.llm_service import LLMService
from src.services.indexing.embedding_service import EmbeddingService
from src.services.retrieval_and_generation.vector_search_service import VectorSearchService
from src.services.retrieval_and_generation.rag_service import RAGService
from src.repository.chromaDB_repo import ChromaRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("integracao_test")

def inicializar_sistema():
    """
    Inicializa os componentes do sistema para teste de integração
    
    Returns:
        RAGService: Serviço RAG configurado
    """
    # Validação de configurações
    Config.validate()
    
    # Configuração dos callbacks para debug
    callbacks = []
    if Config.DEBUG_MODE:
        callbacks.append(StdOutCallbackHandler())
        callbacks.append(ConsoleCallbackHandler())
    callback_manager = CallbackManager(handlers=callbacks)
    
    # Criação dos clientes AWS
    _, bedrock_client, _ = Config.get_aws_clients()
    
    # Inicialização dos serviços e repositórios
    embedding_service = EmbeddingService(
        bedrock_client=bedrock_client,
        model_id=Config.EMBEDDING_MODEL_ID
    )
    
    chroma_repository = ChromaRepository(
        embedding_function=embedding_service.get_embeddings(),
        collection_name=Config.CHROMA_COLLECTION,
        chroma_path=Config.CHROMA_LOCAL_PATH
    )
    
    vector_search_service = VectorSearchService(
        chroma_repository=chroma_repository,
        embedding_service=embedding_service
    )
    
    llm_service = LLMService(
        bedrock_client=bedrock_client,
        callbacks=callbacks
    )
    
    rag_service = RAGService(
        vector_search_service=vector_search_service,
        llm_service=llm_service,
        max_context_docs=Config.MAX_CONTEXT_DOCS
    )
    
    return rag_service

def executar_consulta(rag_service, consulta, historico_chat=None):
    """
    Executa uma consulta no sistema
    
    Args:
        rag_service: Serviço RAG configurado
        consulta: Texto da consulta
        historico_chat: Histórico de chat opcional
            
    Returns:
        dict: Resultado do processamento da consulta
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Executando consulta: '{consulta}'")
    inicio_processo = time.time()
    
    try:
        resultado = rag_service.process_query(consulta, historico_chat)
        
        tempo_total = time.time() - inicio_processo
        logger.info(f"[{request_id}] Consulta processada em {tempo_total:.4f}s")
        
        return {
            "request_id": request_id,
            "execution_time": round(tempo_total, 4),
            **resultado
        }
    except Exception as e:
        logger.error(f"[{request_id}] Erro ao processar consulta: {str(e)}", exc_info=True)
        
        tempo_total = time.time() - inicio_processo
        return {
            "status": "error",
            "request_id": request_id,
            "execution_time": round(tempo_total, 4),
            "error": str(e)
        }

# Executar teste de integração
if __name__ == "__main__":
    print("Iniciando teste de integração do sistema RAG...")
    rag_service = inicializar_sistema()
    
    # Exemplo de consulta para teste
    consulta = "Quem é Willy?"
    
    print(f"\nConsulta de teste: '{consulta}'")
    
    resultado = executar_consulta(rag_service, consulta)
    
    print("\nResultado do teste:")
    print(f"ID da requisição: {resultado.get('request_id')}")
    print(f"Tempo de execução: {resultado.get('execution_time')}s")
    print(f"Resposta: {resultado.get('answer', 'Nenhuma resposta')}")
    
    print("\nTeste de integração concluído.")