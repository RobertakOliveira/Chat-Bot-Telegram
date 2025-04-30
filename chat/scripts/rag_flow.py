import time
from chat.core.query_embeddings import get_query_embedding
from chat.core.retriever import ChromaRetriever
from chat.core.generator import generate_response
from typing import List, Dict
from chat.utils.logger import get_logger

logger = get_logger("rag_flow")

class RAGFlow:
   def __init__(self, collection_name: str = "collection_docs"):  # Nome fixo da coleção
       """
       Fluxo RAG simplificado com nome de coleção fixo
       """
       # Inicializa o retriever com a coleção ChromaDB especificada
       self.retriever = ChromaRetriever(collection_name=collection_name)
       logger.info("🚀 RAGFlow inicializado com sucesso")
      
   def retrieve(self, query: str, doc_type: str = None, case_id: str = None, n_results: int = 3) -> str:
       """
       Executa o fluxo completo de recuperação e geração de resposta
      
       Args:
           query: Pergunta do usuário
           doc_type: Tipo do documento (se fornecido)
           case_id: ID do caso (se fornecido)
           n_results: Número de resultados a retornar
          
       Returns:
           Resposta gerada pelo modelo
       """
       logger.info("🟢 Iniciando execução do RAGFlow...")
       logger.info(f"❓ Processando query: '{query}'")
       start_time = time.time()  # Início da contagem de tempo para medir performance
       try:
           # Converte a pergunta em um vetor numérico (embedding) para busca semântica
           query_embedding = get_query_embedding(query)
           logger.info(f"🔢 Embedding da query gerado com sucesso: {query_embedding[:5]}...")  # Mostra só os 5 primeiros valores do embedding
           
           # Registra os filtros que serão usados na busca de documentos
           logger.info(f"🧩 Filtros aplicados — doc_type: {doc_type}, case_id: {case_id}")
          
           # Usa os embeddings e filtros para encontrar documentos semelhantes semanticamente
           retrieved_docs = self.retriever.retrieve_documents(query_embedding, doc_type=doc_type, case_id=case_id, n_results=n_results)
          
           # Verifica se foram encontrados documentos relevantes
           if not retrieved_docs:
               logger.warning("⚠️ Nenhum documento relevante encontrado para a consulta.")
               return "A informação solicitada não está disponível nos documentos analisados."
          
           # Log do número de documentos encontrados
           logger.info(f"📚 {len(retrieved_docs)} documentos encontrados.")
           
           # Registra os primeiros 300 caracteres de cada documento para fins de debug
           logger.info("📄 Conteúdo dos documentos recuperados:")
           for i, doc in enumerate(retrieved_docs):
               logger.info(f"📝 Doc {i+1}: {doc.get('content')[:300]}...")  # Limita a 300 chars para não sobrecarregar os logs
          
           # Concatena todos os documentos em um único contexto para enviar ao modelo
           context = " ".join([doc['content'] for doc in retrieved_docs])
          
           # Envia o contexto e a pergunta original para o LLM gerar uma resposta coerente
           response = generate_response(context, query)
           return response
           
       except Exception as e:
           # Captura e registra qualquer erro ocorrido durante o processo
           logger.exception(f"💥 Erro inesperado no fluxo RAG: {e}")
           return "A informação solicitada não está disponível no documento analisado."
           
       finally: # Bloco executado sempre, independente de sucesso ou erro
           # Calcula e registra o tempo total de execução para análise de performance
           elapsed_time = time.time() - start_time
           logger.info(f"🏁 Execução finalizada! ⏱️ Tempo total: {elapsed_time:.2f} segundos")