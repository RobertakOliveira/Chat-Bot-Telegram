import logging
import time
import uuid

import sys
sys.path.insert(0, '../src/')
from services.generate_embedding_query_service import GenerateEmbeddingQueryService

logger = logging.getLogger("rag_service")

class RAGService:
    def __init__(self, vector_search_service, llm_service, max_context_docs=5):
        """
        Inicializa o serviço RAG
        
        Args:
            vector_search_service: Serviço de busca vetorial
            llm_service: Serviço LLM
            max_context_docs: Número máximo de documentos para o contexto
        """
        self.vector_search_service = vector_search_service
        self.llm_service = llm_service
        self.max_context_docs = max_context_docs
        self.geqs = GenerateEmbeddingQueryService(self.llm_service.llm)
    
    def process_query(self, query, chat_id):
        """
        Processa uma query usando RAG
        
        Args:
            query: Texto da query
            chat_history: Histórico de chat opcional
            
        Returns:
            dict: Resultado do processamento
        """
        query_id = str(uuid.uuid4())[:8]
        logger.info(f"[{query_id}] Iniciando processamento de query: '{query}'")
        process_start = time.time()
        
        try:
            chat_history = self.llm_service.graph_service.get_chat_history(chat_id)

            geqs_result = self.geqs.generate_query(chat_history, query) if len(chat_history) > 0 else {"worth_searching": True, "refined_query": query}

            # Busca documentos relevantes
            docs = []
            document_sources = []
            context = '--- Nenhum trecho adicional de algum documento pareceu relevante para a pergunta do usuário ---'
            
            # GEQS approved searching documents.
            if geqs_result['worth_searching']:
                query = geqs_result['refined_query']
                docs = self.vector_search_service.similarity_search(query, k=self.max_context_docs)
            
                # Log dos documentos usados
                logger.info(f"[{query_id}] Documentos selecionados para o contexto:")
                for i, doc in enumerate(docs):
                    source = "Desconhecido"
                    if hasattr(doc, 'metadata') and doc.metadata:
                        source = doc.metadata.get('source', doc.metadata.get('file_path', 'Desconhecido'))
                    document_sources.append(source)
                    logger.info(f"[{query_id}]   {i+1}. {source}")
                
                # Construindo o contexto
                logger.debug(f"[{query_id}] Construindo contexto a partir de {len(docs)} documentos")            
                context_start = time.time()
                context = "\n\n".join([doc.page_content for doc in docs])
                logger.debug(f"[{query_id}] Contexto construído com {len(context)} caracteres")
                context_time = time.time() - context_start
            
            # Cria o prompt RAG
            logger.debug(f"[{query_id}] Criando prompt RAG")
            messages = self.llm_service.create_rag_prompt(context, query)
            
            # Gera a resposta
            logger.info(f"[{query_id}] Gerando resposta com LLM...")
            llm_start = time.time()
            response = self.llm_service.generate_response(messages, chat_id, query)
            llm_time = time.time() - llm_start
            logger.info(f"[{query_id}] ✅ Resposta gerada com sucesso em {llm_time:.4f}s")
            
            # Tempo total de processamento
            total_time = time.time() - process_start
            logger.info(f"[{query_id}] 🏁 Processamento completo em {total_time:.4f}s")
            
            return {
                "response": response,
                "context_docs": len(docs),
                "document_sources": document_sources,
                "model_used": self.llm_service.model_id,
                "processing_time": round(total_time, 4),
                "metrics": {
                    "llm_time": round(llm_time, 4),
                    "context_docs": len(docs)
                }
            }
        except Exception as e:
            logger.error(f"[{query_id}] ❌ Erro ao processar query: {str(e)}", exc_info=True)
            raise 