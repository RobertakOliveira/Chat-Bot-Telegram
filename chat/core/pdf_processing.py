# chat/core/pdf_processing.py
import os
import re
from re import sub, search, IGNORECASE
import tempfile
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chat.utils.aws_clients import s3_client
from chat.utils.config import pdf_config
from chat.utils.logger import logger

# ======================================================================


class LegalTextProcessor:
    """Processador simplificado para documentos jurídicos"""

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=pdf_config.CHUNK_SIZE,
            chunk_overlap=pdf_config.CHUNK_OVERLAP,
            separators=pdf_config.LEGAL_SEPARATORS
        )

    def _clean_text(self, text: str) -> str:
        """Limpeza básica do texto"""
        patterns = r'(Página\s+\d+\s+de\s+\d+|Fl\.\s*\d+.*|Documento\s+eletrônico.*)'
        return re.sub(patterns, '', text, flags=re.IGNORECASE).strip()

    def process_pdf(self, file_path: str) -> List[Document]:
        """Processamento robusto de PDFs jurídicos"""
        try:
            loader = PyPDFLoader(file_path, mode="page")
            pages = loader.load()

            cleaned_pages = []
            for page in pages:
                try:
                    page.page_content = self._clean_text(page.page_content)
                    cleaned_pages.append(page)
                except Exception as e:
                    logger.warning(f"🚨 Erro processando página: {str(e)}")
                    continue

            return self.splitter.split_documents(cleaned_pages)
        except Exception as e:
            logger.error(f"❌ Falha no processamento do PDF: {str(e)}")
            return []


def _extract_path_metadata(s3_key: str) -> Dict[str, str]:
    """Extrai metadados essenciais do caminho S3"""
    filename = os.path.basename(s3_key).lower().replace('.pdf', '')

    # Padrão para NÚMERO-TIPODOCUMENTO
    match = search(r'^\d+-(.+)$', filename)

    if match:
        doc_type = match.group(1).replace('-', ' ').title()
    else:
        doc_type = "outros"

    return {
        'doc_type': doc_type,
        'source': s3_key
    }


def process_pdf_from_s3(bucket: str, key: str) -> List[Document]:
    """Processa um PDF do S3 com validações, extração de texto, metadados jurídicos e enriquecimento"""

    # 🧪 Validação inicial: arquivo existe e tem tamanho mínimo
    try:
        head = s3_client.head_object(Bucket=bucket, Key=key)
        if head.get('ContentLength', 0) < 1024:  # 1KB mínimo
            logger.warning(
                f"Ignorando arquivo pequeno: {key} ({head['ContentLength']} bytes)")
            return []
    except Exception as e:
        logger.error(f"❌ Falha ao acessar {key}: {str(e)}")
        return []

    # 📥 Download e processamento
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
        try:
            s3_client.download_file(bucket, key, tmp_file.name)

            # Verificação de integridade
            if os.path.getsize(tmp_file.name) == 0:
                raise ValueError(f"Arquivo corrompido: {key}")

            # 📄 Carregamento do PDF
            processor = LegalTextProcessor()

            # 🔍 Processamento do texto
            raw_documents = processor.process_pdf(tmp_file.name)

            # Limpeza e filtragem dos documentos
            processed_docs = []
            for doc in raw_documents:
                # Filtra chunks muito curtos
                if len(doc.page_content) < pdf_config.MIN_CHUNK_LENGTH:
                    continue

                # Normaliza metadados
                clean_metadata = {
                    "doc_type": _extract_path_metadata(key)["doc_type"],
                    "source": key,
                    "page": doc.metadata.get("page", 0) + 1
                }

                processed_docs.append(Document(
                    page_content=doc.page_content,
                    metadata=clean_metadata
                ))

            logger.info(
                f"⏳ Processado: {key} → {len(processed_docs)} chunks")
            return processed_docs

        except Exception as e:
            logger.error(f"🚨 Erro processando {key}: {str(e)}")
            return []

        finally:
            # Limpeza garantida do arquivo temporário
            try:
                os.remove(tmp_file.name)
            except Exception as e:
                logger.warning(
                    f"❌ Falha ao limpar arquivo temporário: {str(e)}")


def list_pdfs_in_bucket(bucket: str) -> List[Dict]:
    """Lista todos os PDFs no bucket com paginação"""
    pdfs = []
    paginator = s3_client.get_paginator('list_objects_v2')

    for page in paginator.paginate(Bucket=bucket, Prefix="juridicos/"):
        for obj in page.get('Contents', []):
            if obj['Key'].lower().endswith('.pdf'):
                pdfs.append({  # ✅ Apenas coleta metadados
                    'bucket': bucket,
                    'key': obj['Key']
                })
    return pdfs


def process_all_pdfs_in_bucket(bucket: str) -> List[Document]:
    """Processa todos os PDFs encontrados no bucket de forma recursiva"""
    all_docs = []
    pdf_files = list_pdfs_in_bucket(bucket)  # ✅ Lista apenas arquivos

    for pdf in pdf_files:
        try:
            docs = process_pdf_from_s3(
                pdf['bucket'], pdf['key'])  # ✅ Processa uma vez
            all_docs.extend(docs)
            logger.info(f"✅ {pdf['key']} → {len(docs)} chunks\n")
        except Exception as e:
            logger.error(f"🚨 Erro processando {pdf['key']}: {str(e)}")

    logger.info(
        f"📚 Total processado: {len(all_docs)} chunks de {len(pdf_files)} PDFs")
    return all_docs
