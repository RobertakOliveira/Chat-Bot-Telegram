# chat/scripts/ingest.py

import sys
import os
import time
import random
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3  # <-- Novo import necessário
import botocore  # <-- Novo import para tratamento de exceções

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chat.core.pdf_processing import process_pdf_from_s3, list_pdfs_in_bucket
from chat.core.vector_store import initialize_chroma_instance
from chat.utils.aws_clients import s3_client
from chat.utils.config import config
from chat.utils.logger import get_logger
from langchain.schema import Document
from chat.core.upload_chroma_to_s3 import upload_chroma_to_s3

logger = get_logger("ingest")
MAX_WORKERS = 4

def generate_collection_name():
    return f"collection_{random.randint(10000, 99999)}"

def compress_chroma_db(collection_name):
    """Compacta o diretório do ChromaDB em um .tar.gz"""
    timestamp = int(time.time())
    output_file = f"chroma_db_{timestamp}.tar.gz"  # <-- agora com timestamp
    source_dir = config.CHROMA_DB_PATH

    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

    print(f"📦 Banco Chroma compactado como: {output_file}")
    return output_file

def verify_upload(bucket, key):
    """Verifica se o upload para S3 foi bem-sucedido"""
    try:
        head = s3_client.head_object(Bucket=bucket, Key=key)
        if head['ContentLength'] > 0:
            return True
    except Exception as e:
        logger.error(f"Erro na verificação de upload para {key}: {str(e)}")
    return False

# Função para esperar o bucket ficar disponível
def wait_for_bucket(s3_client, bucket_name, timeout_seconds=30):
    """Espera até o bucket S3 estar disponível, ou dá timeout."""
    start_time = time.time()
    while True:
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' encontrado!")
            return
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                # Bucket não existe ainda
                if time.time() - start_time > timeout_seconds:
                    raise Exception(f"⏰ Timeout: Bucket '{bucket_name}' não disponível após {timeout_seconds} segundos.")
                print(f"⌛ Aguardando bucket '{bucket_name}' ficar pronto...")
                time.sleep(3)  # Espera 3 segundos e tenta de novo
            else:
                # Outro erro, melhor relançar
                raise

def ingest_pdfs(bucket_name: str, collection_name: str):
    """Processa todos os PDFs do bucket S3 e indexa no ChromaDB."""
    logger.info(f"🚀 Iniciando ingestão do bucket: {bucket_name}")
    start_total = time.time()

    try:
        # Espera o bucket ficar disponível
        wait_for_bucket(boto3.client('s3'), bucket_name)

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

        # 🔵 NOVA PARTE: Compactar e enviar ChromaDB + ready_flag
        logger.info("🔄 Compactando e enviando ChromaDB para o S3...")

        compressed_file = None
        ready_flag_file = 'ready_flag'

        try:
            # Compacta o ChromaDB
            compressed_file = compress_chroma_db(collection_name)
            
            # Faz upload do ChromaDB compactado
            s3 = boto3.client('s3')
            s3.upload_file(compressed_file, config.S3_BUCKET_CHROMADB, compressed_file)

            # Verifica upload
            if verify_upload(config.S3_BUCKET_CHROMADB, compressed_file):
                logger.info("✅ Upload do ChromaDB verificado com sucesso!")
            else:
                logger.error("❌ Falha na verificação do upload do ChromaDB.")
                raise Exception("Falha na verificação de upload.")

            # Cria o arquivo ready_flag
            with open(ready_flag_file, 'w') as f:
                f.write('ready')

            # Faz upload do ready_flag
            s3.upload_file(ready_flag_file, config.S3_BUCKET_CHROMADB, ready_flag_file)

            # Verifica upload do ready_flag
            if verify_upload(config.S3_BUCKET_CHROMADB, ready_flag_file):
                logger.info("✅ Upload do ready_flag verificado com sucesso!")
            else:
                logger.error("❌ Falha na verificação do upload do ready_flag.")
                raise Exception("Falha na verificação de upload do ready_flag.")

            logger.info("✅ ChromaDB e ready_flag enviados para S3 com sucesso!")

        except Exception as e:
            logger.error(f"❌ Falha ao enviar ChromaDB ou ready_flag para o S3: {str(e)}")
            raise

        finally:
            # Limpa arquivos temporários
            if compressed_file and os.path.exists(compressed_file):
                os.remove(compressed_file)
            if os.path.exists(ready_flag_file):
                os.remove(ready_flag_file)
            logger.info("🧹 Arquivos temporários removidos.")

    except Exception as e:
        logger.error(f"🔥 Falha crítica: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("🛠️ Iniciando ingestão de PDFs...")
    collection_name = generate_collection_name()
    print(f"Nome da coleção gerado: {collection_name}")
    ingest_pdfs(config.S3_BUCKET_NAME, collection_name)
