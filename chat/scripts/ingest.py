# chat/scripts/ingest.py

import sys
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chat.core.pdf_processing import process_pdf_from_s3, list_pdfs_in_bucket
from chat.core.vector_store import index_documents_in_chroma
from chat.utils.aws_clients import s3_client
from chat.utils.config import config
from chat.utils.logger import get_logger

def generate_collection_name():
    return f"collection_{random.randint(10000, 99999)}"

collection_name = generate_collection_name()
print(f"Nome da coleção gerado: {collection_name}")


logger = get_logger("ingest")

MAX_WORKERS = 4

def ingest_pdfs(bucket_name: str, collection_name: str):
    """Processa todos os PDFs do bucket S3 e indexa no ChromaDB."""
    logger.info(f"🚀 Iniciando ingestão do bucket: {bucket_name}")
    
    try:
        pdf_files = list_pdfs_in_bucket(bucket_name)
        logger.info(f"📄 Total de PDFs encontrados: {len(pdf_files)}")

        # Gerar um nome de coleção aleatório para este conjunto de PDFs
        collection_name = f"collection_{random.randint(10000, 99999)}"  # Nome da coleção aleatória

        for i, pdf in enumerate(pdf_files, 1):
            logger.info(f"🔍 ({i}/{len(pdf_files)}) Processando: {pdf['key']}")
            
            # Processa o PDF e retorna os documentos com metadados já configurados
            docs = process_pdf_from_s3(pdf['bucket'], pdf['key'])
            if not docs:
                logger.warning(f"⚠️ Nenhum conteúdo em {pdf['key']}")
                continue

            # Agora passamos os textos, metadados e o nome da coleção de forma única
            index_documents_in_chroma(
                texts=[doc.page_content for doc in docs],
                metadatas=[doc.metadata for doc in docs],
                case_id=pdf['key'].split("/")[1],  # Ou outro identificador relevante para o caso
                collection_name=collection_name  # Passando o nome da coleção aqui
            )
            logger.info(f"✔️ {pdf['key']} → {len(docs)} chunks")

        logger.info("🏁 Ingestão concluída com sucesso!")

    except Exception as e:
        logger.error(f"🔥 Falha crítica: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("🛠️ Iniciando ingestão de PDFs...")
    ingest_pdfs(config.S3_BUCKET_NAME, collection_name)