import os
import boto3
import shutil
import logging
import json
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from classe_embedding import BedrockEmbeddings
from langchain_chroma import Chroma

# Configuração de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variáveis de ambiente fornecidas pelo Terraform
INPUT_BUCKET  = os.environ["INPUT_BUCKET"]
INPUT_PREFIX  = os.environ.get("INPUT_PREFIX", "input/chroma_db/")
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "output/chroma_db/")

# Diretórios temporários no Lambda
LOCAL_PDF_DIR = "/tmp/pdf_dataset"
PERSIST_DIR   = "/tmp/chroma_db"

# Cliente S3
s3 = boto3.client("s3")


def download_pdfs_from_s3():
    """
    Faz download recursivo de todos os arquivos .pdf de INPUT_BUCKET/INPUT_PREFIX
    para LOCAL_PDF_DIR.
    """
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=INPUT_BUCKET, Prefix=INPUT_PREFIX):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.lower().endswith(".pdf"):
                continue
            rel_path = key[len(INPUT_PREFIX):]
            local_path = os.path.join(LOCAL_PDF_DIR, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(INPUT_BUCKET, key, local_path)
            logger.info(f"✅ Downloaded s3://{INPUT_BUCKET}/{key} → {local_path}")


def build_chroma_index():
    """
    Carrega os PDFs de LOCAL_PDF_DIR, quebra em chunks e cria o índice Chroma
    persistindo em PERSIST_DIR.
    """
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    os.makedirs(PERSIST_DIR, exist_ok=True)

    loader = DirectoryLoader(LOCAL_PDF_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    logger.info(f"📄 {len(documents)} documentos PDF carregados.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = splitter.split_documents(documents)
    logger.info(f"✂️ {len(docs)} chunks gerados.")

    embeddings = BedrockEmbeddings()
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=PERSIST_DIR)
    logger.info(f"✅ Índice Chroma criado em: {PERSIST_DIR}")
    return vectorstore


def upload_chroma_to_s3():
    """
    Faz upload recursivo dos arquivos em PERSIST_DIR
    para OUTPUT_BUCKET/OUTPUT_PREFIX.
    """
    for root, _, files in os.walk(PERSIST_DIR):
        for filename in files:
            local_path = os.path.join(root, filename)
            rel_path = os.path.relpath(local_path, PERSIST_DIR)
            s3_key = os.path.join(OUTPUT_PREFIX, rel_path).replace("\\", "/")
            s3.upload_file(local_path, OUTPUT_BUCKET, s3_key)
            logger.info(f"✅ Uploaded {local_path} → s3://{OUTPUT_BUCKET}/{s3_key}")


def handler(event, context):
    """
    Lambda handler para ser chamado via API Gateway (Proxy Integration).
    Faz download, gera embeddings e retorna um JSON de status.
    """
    logger.info(f"🚀 Received event: {json.dumps(event)}")

    try:
        # Limpa e prepara diretórios temporários
        for d in (LOCAL_PDF_DIR, PERSIST_DIR):
            if os.path.exists(d):
                shutil.rmtree(d)
            os.makedirs(d, exist_ok=True)

        # Fluxo principal
        download_pdfs_from_s3()
        build_chroma_index()
        upload_chroma_to_s3()

        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"message": "✅ Embeddings gerados com sucesso"})
        }
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        response = {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

    return response
