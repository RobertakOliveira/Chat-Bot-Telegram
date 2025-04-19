# chat/core/pdf_processing.py
import os
import re
from re import sub, search, IGNORECASE
import tempfile
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chat.utils.aws_clients import s3_client
from chat.utils.config import pdf_config
from chat.utils.logger import get_logger

logger = get_logger("pdf_processing")

# ======================================================================


class LegalTextProcessor:
    """Processador simplificado para documentos jurídicos"""

    def __init__(self):
        """Inicializa o processador com configurações específicas"""
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=pdf_config.CHUNK_SIZE,
            chunk_overlap=pdf_config.CHUNK_OVERLAP,
            separators=pdf_config.LEGAL_SEPARATORS,
            keep_separator=True,
            length_function=len,
            is_separator_regex=True
        )

    def _clean_text(self, text: str) -> str:
        """Limpeza básica do texto"""
        # Extrai elementos importantes que devem ser preservados
        preserved = []
        for pattern in pdf_config.LEGAL_PRESERVE_PATTERNS:
            preserved.extend(pattern.findall(text))

        cleaned_text = text
        # Remove elementos irrelevantes definidos na config
        for pattern in pdf_config.LEGAL_IGNORE_PATTERNS:
            matches = pattern.findall(cleaned_text)
            if matches:
                logger.info(f"🔍 Removendo padrões irrelevantes: {matches}")
            cleaned_text = pattern.sub('', cleaned_text)

        # Recompõe o texto limpo com os elementos preservados no final
        if preserved:
            preserved_text = '\n' + '\n'.join(preserved)
            cleaned_text = cleaned_text.strip() + preserved_text
        else:
            cleaned_text = cleaned_text.strip()

        return cleaned_text.strip()

    def process_pdf(self, file_path: str) -> List[Document]:
        """Carrega e processa um PDF, retornando os textos limpos e divididos em chunks"""
        try:
            # Carrega o PDF, página por página
            loader = PyPDFLoader(file_path, mode="page")
            pages = loader.load()

            cleaned_pages = []
            for page in pages:
                try:
                    # Aplica limpeza em cada página
                    page.page_content = self._clean_text(page.page_content)
                    cleaned_pages.append(page)
                except Exception as e:
                    logger.warning(f"🚨 Erro processando página: {str(e)}")
                    continue

            # Divide o conteúdo em chunks com base nos separadores
            documents = self.splitter.split_documents(cleaned_pages)
            return documents

        except Exception as e:
            logger.error(f"❌ Falha no processamento do PDF: {str(e)}")
            return []
# ======================================================================


def _extract_path_metadata(s3_key: str) -> Dict[str, str]:
    """Extrai metadados essenciais do caminho S3"""
    filename = os.path.basename(s3_key).lower().replace('.pdf', '')
    match = re.search(r'^\d+-(.+)$', filename)
    doc_type = match.group(1).replace('-', ' ').title() if match else "outros"
    return {'doc_type': doc_type, 'source': s3_key}

# ======================================================================


def process_pdf_from_s3(bucket: str, key: str) -> List[Document]:
    """
    Fluxo completo de processamento de PDF vindo do S3:
    - Valida tamanho
    - Faz download para arquivo temporário
    - Carrega e limpa o texto
    - Divide em chunks
    - Enriquecer com metadados
    """

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

     # 📥 Cria um arquivo temporário e baixa o conteúdo do S3
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
        try:
            logger.info(f"📥 Carregando PDF: {key}")
            s3_client.download_file(bucket, key, tmp_file.name)

            # Verifica se o arquivo está vazio ou corrompido
            if os.path.getsize(tmp_file.name) == 0:
                raise ValueError(f"Arquivo muito pequeno ou corrompido: {key}")

            # 📄 Cria processador e inicia limpeza + chunking
            processor = LegalTextProcessor()
            logger.info(
                f"⏲️  Iniciando limpeza e divisão do texto para: {key}")

            # 🔍 Processamento do texto
            raw_documents = processor.process_pdf(tmp_file.name)

            # 🧠 Pegando total de páginas distintas
            num_paginas = len(set(doc.metadata.get(
                "page", 0) + 1 for doc in raw_documents))

            logger.info(f"📄 PDF carregado com {num_paginas} página(s)")
            logger.info(
                f"🗃️  Documentos processados e divididos em {len(raw_documents)} chunks para: {key}")

            # 🔍 Limpa e filtra os chunks válidos
            processed_docs = []
            for doc in raw_documents:
                # Ignora textos curtos que podem ser irrelevantes
                if len(doc.page_content or "") < pdf_config.MIN_CHUNK_LENGTH:
                    # Log de aviso para o chunk muito curto
                    logger.warning(
                        f"⚠️ Chunk muito curto, ignorado: página {doc.metadata.get('page')}")

                    # Log de depuração para mostrar o conteúdo ignorado
                    # Exibe os primeiros 500 caracteres do chunk
                    logger.debug(
                        f"Conteúdo ignorado na página {doc.metadata.get('page')}: {doc.page_content[:2000]}")

                    continue

                # Adiciona metadados complementares úteis para rastreamento
                clean_metadata = {
                    "doc_type": _extract_path_metadata(key)["doc_type"],
                    "source": key,
                    "page": doc.metadata.get("page", 0) + 1
                }

                doc.metadata = clean_metadata
                processed_docs.append(doc)

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
                    f"🧹 Falha ao limpar arquivo temporário: {str(e)}")
# ======================================================================


def list_pdfs_in_bucket(bucket: str) -> List[Dict]:
    """Lista todos os PDFs no bucket com paginação"""
    pdfs = []
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=pdf_config.PDF_PREFIX):
        for obj in page.get('Contents', []):
            if obj['Key'].lower().endswith('.pdf'):
                # ✅ Apenas coleta metadados
                pdfs.append({'bucket': bucket, 'key': obj['Key']})
    return pdfs

# ======================================================================


def process_all_pdfs_in_bucket(bucket: str) -> List[Document]:
    """Processa todos os PDFs encontrados no bucket de forma recursiva"""
    all_docs = []
    pdf_files = list_pdfs_in_bucket(bucket)  # ✅ Lista apenas arquivos

    for i, pdf in enumerate(pdf_files, 1):
        try:
            logger.info(f"📝 ({i}/{len(pdf_files)}) Processando: {pdf['key']}")
            docs = process_pdf_from_s3(pdf['bucket'], pdf['key'])

            all_docs.extend(docs)
            logger.info(f"✅ {pdf['key']} → {len(docs)} chunks\n")

        except Exception as e:
            logger.error(f"🚨 Erro processando {pdf['key']}: {str(e)}")

    logger.info(f"📚 Total processado: {len(all_docs)} chunks")
    return all_docs
