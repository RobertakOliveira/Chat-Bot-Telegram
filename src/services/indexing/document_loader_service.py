import os
import logging
from langchain_community.document_loaders import PyPDFLoader

logger = logging.getLogger("document_service")

class DocumentService:
    def __init__(self, s3_service, embedding_service, chroma_repository):
        """
        Inicializa o serviço de processamento de documentos
        
        Args:
            s3_service: Serviço S3
            embedding_service: Serviço de embeddings
            chroma_repository: Repositório ChromaDB
        """
        self.s3_service = s3_service
        self.embedding_service = embedding_service
        self.chroma_repository = chroma_repository
    
    def process_document(self, object_key):
        """
        Processa um documento do S3 e armazena no ChromaDB
        
        Args:
            object_key: Chave do objeto no S3
            
        Returns:
            dict: Resultado do processamento
        """
        try:
            logger.info(f"Processando arquivo: {object_key}")
            
            # Baixa o arquivo temporariamente do S3
            temp_file = f"/tmp/{os.path.basename(object_key)}"
            success = self.s3_service.download_file(object_key, temp_file)
            
            if not success:
                return {"success": False, "error": "Falha ao baixar arquivo do S3"}
            
            # Carrega o documento usando PyPDFLoader
            loader = PyPDFLoader(temp_file)
            documents = loader.load()
            logger.info(f"Documento carregado: {len(documents)} páginas")

            # Enriquece os documentos com metadados
            for doc in documents:
                # Garantir que existe metadata
                if not hasattr(doc, 'metadata'):
                    doc.metadata = {}
                
                # Adiciona informações sobre o documento
                doc.metadata['source'] = object_key
                doc.metadata['file_name'] = os.path.basename(object_key)
                doc.metadata['file_path'] = temp_file
                doc.metadata['s3_path'] = f"s3://{self.s3_service.bucket_name}/{object_key}"
                
                # Adiciona um prefixo ao conteúdo do documento para identificação
                original_content = doc.page_content
                doc.page_content = f"Documento: {object_key}\n\n{original_content}"

            # Divide o texto em chunks
            splits = self.embedding_service.split_documents(documents)
            logger.info(f"Texto dividido em {len(splits)} chunks")

            # Adiciona os documentos ao ChromaDB
            self.chroma_repository.add_documents(splits)
            logger.info("✅ Documento processado e adicionado ao ChromaDB")

            # Remove o arquivo temporário
            os.remove(temp_file)
            
            return {
                "success": True, 
                "pages": len(documents), 
                "chunks": len(splits),
                "document": object_key
            }

        except Exception as e:
            logger.error(f"❌ Erro ao processar {object_key}: {str(e)}")
            # Garante que o arquivo temporário seja removido em caso de erro
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.remove(temp_file)
            return {"success": False, "error": str(e)}
    
    def process_all_documents(self):
        """
        Processa todos os documentos do S3 e armazena no ChromaDB
        
        Returns:
            dict: Resultado do processamento de todos os documentos
        """
        logger.info("=== Iniciando processamento de documentos ===")
        files = self.s3_service.list_files()
        logger.info(f"Total de arquivos encontrados: {len(files)}")
        
        processed_files = []
        failed_files = []
        total_chunks = 0
        
        for object_key in files:
            result = self.process_document(object_key)
            
            if result.get("success", False):
                processed_files.append(object_key)
                total_chunks += result.get("chunks", 0)
            else:
                failed_files.append({
                    "file": object_key, 
                    "error": result.get("error", "Erro desconhecido")
                })
        
        result = {
            "processed_files": processed_files,
            "failed_files": failed_files,
            "total_chunks": total_chunks
        }
        
        logger.info("=== Resumo do Processamento ===")
        logger.info(f"Arquivos processados: {len(processed_files)}")
        logger.info(f"Arquivos com erro: {len(failed_files)}")
        logger.info(f"Total de chunks: {total_chunks}")
        
        return result 