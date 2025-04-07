# chat/core/pdf_processing.py
import os
import re
import tempfile
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chat.utils.aws_clients import s3_client
from chat.core.bedrock_embeddings import BedrockEmbeddingHandler
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


def process_pdf_from_s3(bucket: str, key: str) -> Dict[str, Any]:
    """Processa um PDF do S3 e retorna estrutura pronta para embeddings"""
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
        s3_client.download_file(bucket, key, tmp_file.name)
        processor = LegalTextProcessor()
        documents = processor.process_pdf(tmp_file.name)

        return {
            "documents": documents,
            "source": key,
            "bucket": bucket
        }


def generate_embeddings_for_pdfs(bucket: str, prefix: str = "") -> None:
    """Processa todos os PDFs no bucket e gera embeddings"""
    pdfs = [obj["Key"] for obj in s3_client.list_objects(Bucket=bucket, Prefix=prefix).get("Contents", [])
            if obj["Key"].lower().endswith(".pdf")]

    if not pdfs:
        print("Nenhum PDF encontrado para processamento")
        return

    embedding_generator = BedrockEmbeddingHandler()

    for pdf_key in pdfs:
        print("===========================================")
        print(f"\nIniciando processamento do PDF: {pdf_key}")
        print("===========================================")
        try:
            result = process_pdf_from_s3(bucket, pdf_key)

            # Mantém a estrutura original de pastas, apenas troca "juridicos" por "juridicos-embeddings"
            embedding_base_path = pdf_key.replace(
                "juridicos/", "juridicos-embeddings/").replace(".pdf", "")

            for i, doc in enumerate(result["documents"]):
                # Nome do arquivo mantendo o padrão anterior
                s3_path = f"{embedding_base_path}_p{doc.metadata['page_number']}_c{i}.json"

                embedding_generator.generate_embedding(
                    text=doc.page_content,
                    s3_bucket_name=bucket,
                    final_path=s3_path,
                    metadata=doc.metadata
                )
                print(f"Embedding salvo em: s3://{bucket}/{s3_path}")

        except Exception as e:
            print(f"Erro processando {pdf_key}: {str(e)}")
            continue
