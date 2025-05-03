import logging
import time
import uuid

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
            # Busca documentos relevantes
            docs = self.vector_search_service.similarity_search(query, k=self.max_context_docs)
            
            # Log dos documentos usados
            logger.info(f"[{query_id}] Documentos selecionados para o contexto:")
            document_sources = []
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