import logging
import time
import uuid
import os

logger = logging.getLogger("vector_search_service")

class VectorSearchService:
    def __init__(self, chroma_repository, embedding_service):
        """
        Inicializa o serviço de busca vetorial
        
        Args:
            chroma_repository: Repositório ChromaDB
            embedding_service: Serviço de embeddings
        """
        self.chroma_repository = chroma_repository
        self.embedding_service = embedding_service
    
    def similarity_search(self, query, k=5):
        """
        Realiza busca por similaridade no ChromaDB
        
        Args:
            query: Texto da query
            k: Número de documentos a retornar
            
        Returns:
            list: Lista de documentos relevantes
        """
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"🔍 [{request_id}] Iniciando similarity search com query: '{query}' (k={k})")
        
        # Medição de tempo
        start_time = time.time()
        
        # Acessa o vectorstore
        vectorstore = self.chroma_repository.get_vectorstore()
        
        # Realizando a busca no vectorstore
        search_start = time.time()
        docs = vectorstore.similarity_search(query, k=k)
        search_time = time.time() - search_start
        
        # Calcular o tempo total
        total_time = time.time() - start_time
        
        # Log detalhado dos resultados
        logger.info(f"[{request_id}] ✅ Busca concluída em {total_time:.4f}s (search: {search_time:.4f}s)")
        logger.info(f"[{request_id}] Encontrados {len(docs)} documentos relevantes")
        
        # Processar metadados e detalhar documentos encontrados
        for i, doc in enumerate(docs):
            # Garantir que existe metadata
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
                
            # Extrair o nome do arquivo do conteúdo se não estiver nos metadados
            if 'source' not in doc.metadata and 'file_path' not in doc.metadata:
                content_lines = doc.page_content.splitlines()
                for line in content_lines[:10]:  # Verifica as primeiras linhas
                    if "Arquivo:" in line or "Documento:" in line or "File:" in line:
                        doc.metadata['source'] = line.split(":", 1)[1].strip()
                        break
            
            # Formatar o nome do arquivo para exibição
            source = doc.metadata.get('source', doc.metadata.get('file_path', 'Desconhecido'))
            if source != 'Desconhecido':
                # Extrair apenas o nome do arquivo se for um caminho completo
                source = os.path.basename(source)
                
            # Log de debug com detalhes do documento
            logger.debug(f"[{request_id}] Documento #{i+1}:")
            logger.debug(f"   - Fonte: {source}")
            logger.debug(f"   - Conteúdo ({len(doc.page_content)} caracteres): {doc.page_content[:150]}...")
            if doc.metadata:
                logger.debug(f"   - Metadata completa: {doc.metadata}")
    
        return docs 