# chat/core/pdf_processing.py
import os
import re
import tempfile
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chat.utils.aws_clients import s3_client
from chat.utils.config import config


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
        s3_client.download_file(bucket, key, tmp_file.name)
        processor = LegalTextProcessor()
        return processor.process_pdf(tmp_file.name)


def process_all_pdfs_from_s3(bucket: str, prefix: str = "") -> List[Document]:
    """Processa todos os PDFs no bucket S3 e retorna chunks consolidados"""
    pdfs = [obj["Key"]
            for obj in s3_client.list_objects(Bucket=bucket, Prefix=prefix).get("Contents", [])
            if obj["Key"].lower().endswith(".pdf")]

    all_documents = []

    for pdf_key in pdfs:
        try:
            documents = process_pdf_from_s3(bucket, pdf_key)
            all_documents.extend(documents)
            print(f"Processado: {pdf_key} | Chunks gerados: {len(documents)}")
        except Exception as e:
            print(f"Erro processando {pdf_key}: {str(e)}")
            continue

    return all_documents


def process_single_pdf_from_s3(bucket: str, key: str) -> List[Document]:
    """Processa APENAS 1 PDF do S3 e retorna seus chunks"""
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
        s3_client.download_file(bucket, key, tmp_file.name)
        processor = LegalTextProcessor()
        return processor.process_pdf(tmp_file.name)
