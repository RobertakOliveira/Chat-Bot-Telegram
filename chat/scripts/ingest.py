# chat/scripts/ingest.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chat.core.pdf_processing import process_pdf_from_s3, list_pdfs_in_bucket
from chat.core.vector_store import index_documents_in_chroma
from chat.utils.aws_clients import s3_client
from chat.utils.config import pdf_config
from chat.utils.logger import get_logger
from chat.utils.config import config

logger = get_logger("ingest")

def ingest_pdfs(bucket_name: str):
    logger.info(f"Iniciando ingestão dos PDFs no bucket: {bucket_name}")

    try:
        pdf_files = list_pdfs_in_bucket(bucket_name)
        
        for i, pdf in enumerate(pdf_files, 1):
            logger.info(f"📝 ({i}/{len(pdf_files)}) Processando: {pdf['key']}")
            
            docs = process_pdf_from_s3(pdf['bucket'], pdf['key'])

            if docs:
                texts = [doc.page_content for doc in docs]
                metadatas = [doc.metadata for doc in docs]

                index_documents_in_chroma(texts, metadatas)

                logger.info(f"✅ {pdf['key']} → {len(docs)} chunks indexados no Chroma\n")
            else:
                logger.warning(f"⚠️ {pdf['key']} não gerou chunks")

        logger.info(f"Ingestão concluída para o bucket: {bucket_name}")

    except Exception as e:
        logger.error(f"🚨 Erro durante ingestão: {str(e)}")

if __name__ == "__main__":
    bucket_name = config.S3_BUCKET_NAME
    ingest_pdfs(bucket_name)