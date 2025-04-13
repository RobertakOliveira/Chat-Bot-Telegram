# chat/core/pdf_processing.py
import os
import re
import tempfile
from datetime import datetime
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chat.utils.aws_clients import s3_client
from chat.utils.config import config
import logging
logging.basicConfig(level=logging.INFO)


class LegalTextProcessor:
    """Processador especializado para documentos jurídicos"""

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=[
                "\nArtigo", "\nParágrafo", "\n§", "\nArt. ",
                "\n\n", "\n", " ",
            ]
        )

    def _clean_text(self, text: str) -> str:
        """Normaliza texto jurídico"""
        text = re.sub(r'(\n\s*)+\n+', '\n\n', text)
        text = re.sub(r'(?i)(artigo|art\.)\s*(\d+)', r'Artigo \2', text)
        return text

    def process_pdf(self, file_path: str) -> List[Document]:
        """Processa um PDF completo retornando chunks padronizados"""
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        documents = []

        for page in pages:
            clean_text = self._clean_text(page.page_content)

            chunks = self.splitter.create_documents(
                [clean_text],
                metadatas=[{
                    **page.metadata,
                    "page_number": page.metadata.get("page", 1),
                    "source": os.path.basename(file_path)
                }]
            )
            documents.extend(chunks)

        return documents


def process_pdf_from_s3(bucket: str, key: str) -> List[Document]:
    """Processa um PDF do S3 e retorna lista de documentos (chunks)"""
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
        try:
            s3_client.head_object(Bucket=bucket, Key=key)  # Verifica se existe
            s3_client.download_file(bucket, key, tmp_file.name)

            if not os.path.getsize(tmp_file.name) > 0:  # Verifica se não está vazio
                raise ValueError(f"❌ Arquivo vazio: {key}")

            processor = LegalTextProcessor()
            documents = processor.process_pdf(tmp_file.name)

            # Padroniza metadados
            for doc in documents:
                doc.metadata = {
                    "source": f"s3://{bucket}/{key}",
                    "doc_type": "legal",
                    # Pega direto da página
                    "page": doc.metadata.get("page_number", 1),
                    "pdf_key": key,                        # Chave original no S3
                    "timestamp": datetime.now().isoformat()  # Quando foi processado
                }
            return documents
        except Exception as e:
            logging.error(f"❌ Falha no processamento de {key}: {str(e)}")
            return []  # Retorna lista vazia para continuar batch


def process_all_pdfs_from_s3(bucket: str, prefix: str = "") -> List[Document]:
    """Processa todos os PDFs no bucket S3 (incluindo subpastas) e retorna chunks consolidados"""

    try:
        # 1. Lista todos os objetos no prefixo (incluindo subpastas)
        paginator = s3_client.get_paginator('list_objects_v2')
        pdfs = []

        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                if obj['Key'].lower().endswith('.pdf'):
                    pdfs.append(obj['Key'])

        # 2. Log inicial com contagem real de PDFs encontrados
        logging.info(
            f"🔍 Encontrados {len(pdfs)} PDFs em s3://{bucket}/{prefix}")

        logging.info(
            f"📄 Iniciando processamento de {len(pdfs)} PDFs do bucket {bucket}")

        # 3. Processamento em lote
        all_documents = []
        for pdf_key in pdfs:
            try:
                documents = process_pdf_from_s3(bucket, pdf_key)
                all_documents.extend(documents)
                logging.info(
                    f"📝 Processado: {pdf_key} | Chunks gerados: {len(documents)}")
            except Exception as e:
                logging.error(f"❌ Falha em  {pdf_key}: {str(e)}")
                continue

        logging.info(
            f"✅ Processamento concluído. Total de chunks: {len(all_documents)}")
        return all_documents

    except Exception as e:
        logging.error(f"🚨 Erro ao listar/processar PDFs: {str(e)}")
        return []
