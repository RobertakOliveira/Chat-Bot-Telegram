# chat/core/rag_flow.py
import time
from typing import List, Dict, Optional, Any

from chat.core.retriever import ChromaRetriever
from chat.core.generator import generate_response
from chat.core.query_processing import preprocess_query, UserSession
from chat.utils.logger import get_logger

logger = get_logger("Fluxo de Recuperação e Geração de Respostas Jurídicas (RAG)")


class RAGFlow:
    def __init__(self, collection_name: str = "collection_docs"):
        """
        Fluxo RAG integrado com pré-processamento de consultas
        
        Args:
            collection_name: Nome da coleção no ChromaDB
        """
        # Inicializa o retriever com a coleção ChromaDB especificada
        self.retriever = ChromaRetriever(collection_name=collection_name)
        logger.info("🚀 RAGFlow inicializado com sucesso")
    
    def process_query(self, query: str, user_session: UserSession) -> Dict[str, Any]:
        """
        Pré-processa a consulta do usuário
        
        Args:
            query: Pergunta original do usuário
            user_session: Sessão do usuário contendo histórico de conversa
            
        Returns:
            Dict: Resultado do pré-processamento
        """
        try:
            # Adicionar a pergunta ao histórico de conversa
            user_session.add_message(query)
            
            # Pré-processamento da consulta
            processed_result = preprocess_query(query, user_session)
            
            # Verificar se houve erro no pré-processamento
            if processed_result["status"] == "error":
                logger.error(f"❌ Erro no pré-processamento: {processed_result['error']}")
                raise ValueError(f"Falha no pré-processamento: {processed_result['error']}")
                
            logger.info(f"🔎 Consulta pré-processada com sucesso: {processed_result['refined_query']}")
            return processed_result
            
        except Exception as e:
            logger.error(f"❌ Erro durante o processamento da consulta: {str(e)}")
            raise
    
    def get_relevant_documents(self, query_embedding: List[float], doc_type: str = None, 
                             case_id: str = None, n_results: int = 10) -> List[Dict]:
        """
        Recupera documentos relevantes com base no embedding e filtros
        
        Args:
            query_embedding: Embedding vetorial da consulta
            doc_type: Tipo de documento para filtrar
            case_id: ID do caso para filtrar
            n_results: Número de documentos a retornar
            
        Returns:
            List[Dict]: Lista de documentos recuperados
        """
        try:
            # Registra os filtros que serão usados na busca
            logger.info(f"🧩 Aplicando filtros — doc_type: {doc_type}, case_id: {case_id}")
            
            # Recupera documentos do ChromaDB
            docs = self.retriever.retrieve_documents(
                query_embedding, 
                doc_type=doc_type, 
                case_id=case_id, 
                n_results=n_results
            )
            
            # Log dos documentos recuperados
            if docs:
                logger.info(f"📚 {len(docs)} documentos recuperados com sucesso")
                for i, doc in enumerate(docs):
                    logger.info(f"📄 Doc {i+1}: {doc.get('content')[:300]}...")
            else:
                logger.warning("⚠️ Nenhum documento relevante encontrado")
                
            return docs
            
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar documentos: {str(e)}")
            raise
    
    def generate_answer(self, context: str, query: str) -> str:
        """
        Gera uma resposta com base no contexto e na consulta
        """
        try:
            logger.info(f"🧠 Gerando resposta para consulta: {query[:100]}...")
            response = generate_response(context, query)
            
            # Verificação para impedir respostas negativas quando há documentos relevantes
            if "não está disponível" in response or "não contém informações" in response:
                # Verifica se os termos da consulta aparecem no contexto
                query_terms = query.lower().split()
                relevant_terms_in_context = [term for term in query_terms 
                                            if term in context.lower() and len(term) > 3]
                
                if relevant_terms_in_context:
                    logger.warning("⚠️ Modelo retornou 'informação não disponível' mas documentos contêm termos relevantes")
                    # Tenta novamente com prompt mais explícito
                    enhanced_prompt = f"IMPORTANTE: Os documentos fornecidos CONTÊM informações sobre {', '.join(relevant_terms_in_context)}. "
                    enhanced_prompt += "Extraia e sintetize QUALQUER menção a esses termos, mesmo que fragmentada. "
                    enhanced_prompt += "NÃO responda que a informação não está disponível."
                    
                    # Combinando com o prompt original
                    response = generate_response(context, enhanced_prompt + "\n\n" + query)
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta: {str(e)}")
            raise
    
    def execute(self, query: str, user_session: UserSession, 
               case_id: str = None, n_results: int = 10) -> Dict[str, Any]:
        """
        Executa o fluxo RAG completo encapsulando todo o processamento
        
        Args:
            query: Pergunta original do usuário
            user_session: Sessão do usuário
            case_id: ID do caso (opcional)
            n_results: Número de resultados desejados
            
        Returns:
            Dict: Resposta completa com metadados
        """
        start_time = time.time()
        logger.info(f"🔄 Iniciando execução do RAGFlow para consulta: {query}")
        
        try:
            # 1. Pré-processamento da consulta
            processed = self.process_query(query, user_session)
            
            # 2. Recuperação de documentos relevantes
            docs = self.get_relevant_documents(
                query_embedding=processed["embedding"],
                doc_type=processed["doc_type"],
                case_id=case_id,
                n_results=n_results
            )
            
            # Se não encontrou documentos relevantes
            if not docs:
                return {
                    "answer": "A informação solicitada não está disponível nos documentos analisados.",
                    "sources": [],
                    "confidence": 0.0,
                    "metadata": {
                        "refined_query": processed["refined_query"],
                        "doc_type": processed["doc_type"],
                        "intent": processed["intent"],
                        "processing_time": time.time() - start_time
                    }
                }
            
            # 3. Concatenar documentos para formar o contexto
            context = " ".join([doc['content'] for doc in docs])
            
            # 4. Gerar resposta com base no contexto e na consulta refinada
            answer = self.generate_answer(context, processed["refined_query"])
            
            # 5. Extrair fontes dos documentos (se disponíveis)
            sources = []
            for doc in docs:
                if "title" in doc or "source" in doc:
                    source = doc.get("title") or doc.get("source") or "Documento sem título"
                    if source not in sources:
                        sources.append(source)
            
            # 6. Construir resposta final com metadados
            response = {
                "answer": answer,
                "sources": sources[:5],  # Limita a 5 fontes
                "confidence": 0.85,  # Placeholder - em produção, calcular confiança real
                "metadata": {
                    "refined_query": processed["refined_query"],
                    "doc_type": processed["doc_type"],
                    "intent": processed["intent"],
                    "processing_time": time.time() - start_time
                }
            }
            
            # 7. Registrar resposta no log
            logger.info(f"🏁 RAGFlow executado com sucesso - tempo: {time.time() - start_time:.2f}s")
            
            return response
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.exception(f"💥 Erro no RAGFlow: {str(e)}")
            
            # Retornar erro formatado
            return {
                "answer": "Não foi possível processar sua consulta devido a um erro interno.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e),
                "metadata": {
                    "processing_time": elapsed_time,
                    "error": str(e)
                }
            }