# chat/scripts/ingest.py

import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chat.core.pdf_processing import process_pdf_from_s3, list_pdfs_in_bucket
from chat.core.vector_store import initialize_chroma_instance
from chat.utils.aws_clients import s3_client
from chat.utils.config import config
from chat.utils.logger import get_logger
from langchain.schema import Document

logger = get_logger("ingest")
MAX_WORKERS = 4

def generate_collection_name():
    return f"collection_{random.randint(10000, 99999)}"

def ingest_pdfs(bucket_name: str, collection_name: str):
    """Processa todos os PDFs do bucket S3 e indexa no ChromaDB."""
    logger.info(f"🚀 Iniciando ingestão do bucket: {bucket_name}")
    start_total = time.time()

    try:
        pdf_files = list_pdfs_in_bucket(bucket_name)
        logger.info(f"📄 Total de PDFs encontrados: {len(pdf_files)}")

        chroma = initialize_chroma_instance(collection_name)
        all_docs = []

        def process_single_pdf(pdf):
            start = time.time()
            logger.info(f"🔍 Processando: {pdf['key']}")
            docs = process_pdf_from_s3(pdf['bucket'], pdf['key'])
            if not docs:
                logger.warning(f"⚠️ Nenhum conteúdo extraído de {pdf['key']}")
                return []

            case_id = pdf['key'].split("/")[1]
            for doc in docs:
                if not isinstance(doc.metadata, dict):
                    doc.metadata = {}
                doc.metadata.setdefault("_type", "document")
                doc.metadata["case_id"] = case_id

            duration = time.time() - start
            logger.info(f"✔️ {pdf['key']} → {len(docs)} chunks em {duration:.2f}s")
            return docs

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_single_pdf, pdf) for pdf in pdf_files]
            for future in as_completed(futures):
                docs = future.result()
                all_docs.extend(docs)

        if all_docs:
            logger.info(f"🧠 Gerando embeddings para {len(all_docs)} documentos...")
            chroma.add_documents(documents=all_docs)
            logger.info(f"✅ Indexação concluída na coleção '{collection_name}' com {len(all_docs)} docs.")
        else:
            logger.warning("⚠️ Nenhum documento válido para indexar.")

        logger.info(f"🏁 Ingestão finalizada em {time.time() - start_total:.2f} segundos")

    except Exception as e:
        logger.error(f"🔥 Falha crítica: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("🛠️ Iniciando ingestão de PDFs...")
    collection_name = generate_collection_name()
    print(f"Nome da coleção gerado: {collection_name}")
    ingest_pdfs(config.S3_BUCKET_NAME, collection_name)