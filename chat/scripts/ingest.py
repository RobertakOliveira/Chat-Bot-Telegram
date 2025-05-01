# chat/scripts/ingest.py

import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chat.core.pdf_processing import process_all_pdfs_in_bucket
from chat.core.vector_store import initialize_chroma_instance
from chat.utils.config import config
from chat.utils.logger import get_logger

# Inicializa o logger específico para o processo de ingestão
logger = get_logger("ingest")

def ingest_pdfs(bucket_name: str, collection_name: str):
    """Processa todos os PDFs do bucket S3 e indexa no ChromaDB."""
    logger.info(f"🚀 Iniciando ingestão do bucket: {bucket_name}")
    start_total = time.time()  # Marca o tempo inicial para cálculo da duração total do processo

    try:
        # Inicializa a instância do ChromaDB com o nome da coleção especificada
        chroma = initialize_chroma_instance(collection_name)
        
        # Usa a função process_all_pdfs_in_bucket que já cria uma instância única do processor e processa todos os PDFs do bucket de uma vez
        logger.info(f"🔍 Processando todos os PDFs do bucket: {bucket_name}")
        all_docs = process_all_pdfs_in_bucket(bucket_name)
        
        # Adiciona metadados extras para todos os documentos
        for doc in all_docs:
            # Extrai o ID do caso a partir do caminho do arquivo no metadado 'source'
            source_path = doc.metadata.get('source', '')
            path_parts = source_path.split("/")
            case_id = path_parts[1] if len(path_parts) > 1 else "unknown"
            
            # Garante que metadata seja um dicionário
            if not isinstance(doc.metadata, dict):
                doc.metadata = {}
                
            # Define o tipo de documento como "document", se não estiver definido
            doc.metadata.setdefault("_type", "document")
            
            # Adiciona o ID do caso como metadado
            doc.metadata["case_id"] = case_id

        # Verifica se há documentos para indexar
        if all_docs:
            logger.info(f"🧠 Gerando embeddings para {len(all_docs)} documentos...")
            # Adiciona todos os documentos processados ao ChromaDB, que gerará embeddings
            chroma.add_documents(documents=all_docs)
            logger.info(f"✅ Indexação concluída na coleção '{collection_name}' com {len(all_docs)} docs.")
        else:
            logger.warning("⚠️ Nenhum documento válido para indexar.")

        # Registra o tempo total do processo de ingestão
        logger.info(f"🏁 Ingestão finalizada em {time.time() - start_total:.2f} segundos")
        
    except Exception as e:
        # Captura e registra qualquer erro durante o processo
        logger.error(f"🔥 Falha crítica: {str(e)}")
        # Propaga a exceção para tratamento em nível superior
        raise

# Ponto de entrada para execução direta do script
if __name__ == "__main__":
    logger.info("🛠️ Iniciando ingestão de PDFs...")
    collection_name = "collection_docs"  # Define o nome padronizado da coleção no ChromaDB
    print(f"Nome da coleção gerado: {collection_name}")
    ingest_pdfs(config.S3_BUCKET_NAME, collection_name)  # Inicia o processo de ingestão com o nome do bucket do S3 definido na configuração