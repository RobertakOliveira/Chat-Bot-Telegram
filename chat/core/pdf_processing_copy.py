# chat/core/pdf_processing.py
import os
import re
import tempfile
from datetime import datetime
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chat.utils.aws_clients import s3_client
from chat.utils.config import pdf_config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class LegalMetadataExtractor:
    """Extrai metadados específicos de documentos jurídicos com padrões otimizados"""

    # Padrão que cobre todos os tipos de processos
    PROCESSO_PATTERN = re.compile(
        r'(?:Processo|PROCESSO|RECURSO|AGRAVO|EMBARGOS)[\sNº°:-]*([\d\.-]+)(?:\s*-?\s*[A-Z]{2})?',
        re.IGNORECASE
    )

    # Relator genérico (TJ + STJ)
    RELATOR_PATTERN = re.compile(
        r'(?:Relator|RELATOR)\s*:?\s*(?:Ministr[oa]|Des\.?\s*[A-Z]*)\s+([A-ZÀ-Ú\s]+?)(?:\n|$)',
        re.IGNORECASE
    )

    # Tribunais estaduais e federais
    TRIBUNAL_PATTERNS = [
        (r'TRIBUNAL\s+DE\s+JUSTIÇA\s+(?:DO|DE)\s+([A-Z]+)', 'TJ'),
        (r'TJ-?([A-Z]{2})', 'TJ'),
        (r'Superior\s+Tribunal\s+de\s+Justiça', 'STJ'),
        (r'TRIBUNAL\s+REGIONAL\s+FEDERAL\s+DA\s+(\d+ª?\s+REGIÃO)', 'TRF')
    ]

    # Tipos documentais consolidados
    DOC_TYPE_PATTERNS = {
        'acordão_recorrido': re.compile(r'ACÓRDÃO\s+RECORRIDO', re.IGNORECASE),
        'acordão_embargos': re.compile(r'ACÓRDÃO\s+EMBARGOS', re.IGNORECASE),
        'decisão_admissibilidade': re.compile(r'DECISÃO\s+ADMISSIBILIDADE', re.IGNORECASE),
        'recurso_extraordinário': re.compile(r'RECURSO\s+EXTRAORDINÁRIO', re.IGNORECASE),
        'apelação_cível': re.compile(r'APELAÇÃO\s+CÍVEL', re.IGNORECASE)
    }

    @classmethod
    def _extract_parties(cls, text: str) -> Dict[str, str]:
        """Extrai partes envolvidas (apelante/apelado etc.)"""
        parties = {}
        roles = {
            'apelante': 'parte_ativa',
            'apelado': 'parte_passiva',
            'embargante': 'parte_ativa',
            'embargado': 'parte_passiva',
            'recorrente': 'parte_ativa',
            'recorrido': 'parte_passiva'
        }

        for role, tipo in roles.items():
            match = re.search(
                fr'{role.upper()}\s*:([^\n]+)',
                text,
                re.IGNORECASE
            )
            if match:
                parties[tipo] = match.group(1).strip()

        return parties

    @classmethod
    def extract_from_text(cls, text: str) -> Dict[str, str]:
        """Extrai metadados jurídicos com tratamento de erros"""
        metadata = {}
        try:
            # 1. Extrai número do processo com análise contextual
            metadata.update(cls._extract_process_number(text))

            # 2. Identifica tipo documental com fallback
            metadata['doc_subtype'] = cls._identify_document_type(text)

            # 3. Extrai tribunal com padrão mais abrangente
            metadata.update(cls._extract_court_info(text))
            metadata.update(cls._extract_parties(text))

        except Exception as e:
            logging.warning(f"Falha na extração de metadados: {str(e)}")

        return metadata

    @classmethod
    def _extract_court_info(cls, text: str) -> Dict[str, str]:
        """Versão melhorada para identificar tribunais"""
        patterns = [
            (r'TJ-?([A-Z]{2})', 'TJ'),  # Padrão TJSP/TJ-SP
            (r'Tribunal\s+de\s+Justiça\s+de\s+([A-Z]{2})', 'TJ')
        ]

        for pattern, prefix in patterns:
            match = re.search(pattern, text[:3000], re.IGNORECASE)
            if match:
                return {
                    'jurisdiction': f"{prefix}-{match.group(1).upper()}",
                    'court_level': prefix
                }
        return {'jurisdiction': 'NÃO IDENTIFICADO'}

    @classmethod
    def _extract_process_number(cls, text: str) -> Dict[str, str]:
        """Extrai número do processo com validação"""
        match = cls.PROCESSO_PATTERN.search(
            text[:3000])  # Amplia área de busca
        if match:
            process_num = match.group(1).strip()
            if cls._validate_process_number(process_num):
                return {'process_number': process_num}
        return {}

    @classmethod
    def _validate_process_number(cls, number: str) -> bool:
        """Valida formato básico de número de processo"""
        return len(number) >= 10 and any(c.isdigit() for c in number)

    @classmethod
    def _identify_document_type(cls, text: str) -> str:
        """Identifica tipo documental com prioridade"""
        for doc_type, pattern in cls.DOC_TYPE_PATTERNS.items():
            if pattern.search(text[:1500]):  # Amplia área de busca
                return doc_type
        return 'outros'  # Valor padrão

    @classmethod
    def _extract_court_info(cls, text: str) -> Dict[str, str]:
        """Extrai informações do tribunal"""
        match = cls.TRIBUNAL_PATTERN.search(text[:5000])
        if match:
            return {
                'jurisdiction': f"TJ-{match.group(1).upper()}",
                'court_level': 'TJ'
            }
        return {'jurisdiction': 'NÃO IDENTIFICADO'}


class LegalTextProcessor:
    """Processador otimizado para documentos jurídicos com tratamento especializado"""

    LEGAL_SEPARATORS = [
        "\nArtigo", "\nParágrafo Único", "\nParágrafo", "\n§", "\nArt. ",
        "\nLei nº", "\nDECISÃO", "\nVistos,\s", "\n\n", "\n", " ",
    ]

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=pdf_config.CHUNK_SIZE,
            chunk_overlap=pdf_config.CHUNK_OVERLAP,
            length_function=len,
            separators=self.LEGAL_SEPARATORS,
            keep_separator=True  # Mantém marcadores jurídicos
        )

    def _clean_text(self, text: str) -> str:
        """Normalização avançada de texto jurídico"""

        patterns = [
            r'Documento\s+(?:recebido|eletrônico).*$',
            r'Poder\s+Judiciário.*$',
            r'Fl\.\s*\d+.*$',
            r'Publicação no DJe.*$',
            r'CRIOS©/CRIOS.*$'
        ]

        for pattern in patterns:
            text = re.sub(pattern, '', text,
                          flags=re.MULTILINE | re.IGNORECASE)

        text = self._remove_boilerplate(text)
        text = self._normalize_legal_references(text)
        text = self._fix_line_breaks(text)
        text = re.sub(r'\s+', ' ', text)  # Espaços múltiplos
        text = re.sub(r'-\s+(\w)', r'\1', text)  # Hífens quebrados
        return text.strip()

    def _remove_boilerplate(self, text: str) -> str:
        """Remove cabeçalhos/rodapés comuns em documentos judiciais"""
        patterns = [
            r'(?m)^\s*Tribunal\s+de\s+Justiça.*$\n?',
            r'(?m)^\s*Poder\s+Judiciário.*$\n?',
            r'(?m)^\s*Processo:\s*\d+.*$\n?',
            r'(?m)^\s*Fl\.\s*\d+\s*$',
            r'(?m)^\s*Página\s+\d+\s+de\s+\d+\s*$'
        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        return text

    def _normalize_legal_references(self, text: str) -> str:
        """Padroniza referências legais"""
        replacements = [
            (r'(?i)(artigos?|art\.?)\s*(\d+)', r'Art. \2'),
            (r'(?i)parágrafo\s+único', 'Parágrafo Único'),
            (r'(?i)fls\.?\s*(\d+)', r'fl. \1'),
            (r'-\s+(\w)', r'\1')  # Remove hífens quebrados
        ]
        for pattern, repl in replacements:
            text = re.sub(pattern, repl, text)
        return text

    def _fix_line_breaks(self, text: str) -> str:
        """Corrige quebras de linha inadequadas"""
        text = re.sub(r'(\n\s*)+\n+', '\n\n', text)
        # Preserva quebras após pontuação
        text = re.sub(r'([.;:])\s*\n+', r'\1\n', text)
        return text

    def process_pdf(self, file_path: str) -> List[Document]:
        """Processamento robusto de PDFs jurídicos"""
        try:
            loader = PyPDFLoader(file_path, mode="page")
            pages = loader.load()

            documents = []
            for page in pages:
                try:
                    clean_text = self._clean_text(page.page_content)
                    metadata = self._build_metadata(page, clean_text)
                    chunks = self._split_document(clean_text, metadata)
                    documents.extend(chunks)
                except Exception as e:
                    logging.warning(f"Erro processando página: {str(e)}")
                    continue

            return documents
        except Exception as e:
            logging.error(f"Falha no processamento do PDF: {str(e)}")
            return []

    def _build_metadata(self, page: Document, text: str) -> Dict[str, Any]:
        """Constrói metadados com informações jurídicas"""
        base_meta = {
            **page.metadata,
            "page_number": page.metadata.get("page", 0) + 1,
            "source": os.path.basename(page.metadata.get("source", "")),
            "text_length": len(text),
            "contains_decision": any(
                marker in text[:500]
                for marker in ["DECISÃO", "ACÓRDÃO", "VOTO"]
            ),
            "is_first_page": page.metadata.get("page", 0) == 0,
            "has_legal_references": bool(re.search(r'art\.\s+\d+', text))
        }
        return {**base_meta, **LegalMetadataExtractor.extract_from_text(text)}

    def _split_document(self, text: str, metadata: Dict) -> List[Document]:
        """Divide o texto preservando estrutura jurídica"""
        try:
            return self.splitter.create_documents([text], [metadata])
        except Exception as e:
            logging.error(f"Falha ao dividir documento: {str(e)}")
            return [Document(page_content=text, metadata=metadata)]

        def _remove_boilerplate(self, text: str) -> str:
        """Remove textos repetitivos e cabeçalhos/rodapés padrão"""
        return re.sub(r'Este documento é cópia.*?Tribunal.*?de Justiça.*?\n', '', text, flags=re.IGNORECASE | re.DOTALL)

    def _normalize_legal_references(self, text: str) -> str:
        """Padroniza citações jurídicas comuns"""
        return re.sub(r'Art\.?\s*(\d+)', r'Artigo \1', text)

    def _fix_line_breaks(self, text: str) -> str:
        """Corrige quebras de linha estranhas"""
        return re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    def process(self, text: str) -> List[Document]:
        """Executa o processamento completo com extração e chunking"""
        cleaned_text = self._clean_text(text)
        chunks = self.splitter.create_documents([cleaned_text])
        return chunks


def _extract_path_metadata(s3_key: str) -> Dict[str, str]:
    """Extrai metadados hierárquicos do S3 com validação"""
    parts = [p for p in s3_key.split(
        '/') if p and not p.lower().endswith('.pdf')]

    metadata = {
        'court_level': 'TJ',  # Default para Tribunal de Justiça
        'process_id': None,
        'document_category': None,
        'year': datetime.now().year
    }

    # Padrões para tribunais
    court_patterns = {
        r'tj-?([a-z]{2})': 'TJ',
        r'st[fj]': 'STF/STJ',
        r'trf': 'TRF',
        r'regional-federal': 'TRF'
    }

    for part in parts:
        # Extrai tribunal
        for pattern, level in court_patterns.items():
            if re.search(pattern, part, re.IGNORECASE):
                metadata.update({
                    'jurisdiction': part.upper(),
                    'court_level': level
                })

    # Extrai ano (padrão /2023/)
        year_match = re.search(r'(20\d{2})', part)
        if year_match and 2000 <= int(year_match.group(1)) <= datetime.now().year:
            metadata['year'] = int(year_match.group(1))

    return metadata


def _looks_like_process_id(text: str) -> bool:
    """Heurística para identificar números de processo no caminho"""
    return (any(c.isdigit() for c in text) and len(text)) >= 10


def process_pdf_from_s3(bucket: str, key: str) -> List[Document]:
    """Processa um PDF do S3 com validações, extração de texto, metadados jurídicos e enriquecimento"""

    validation_error = None

    # 🧪 Validação inicial: arquivo existe e tem tamanho mínimo
    try:
        head = s3_client.head_object(Bucket=bucket, Key=key)
        if head.get('ContentLength', 0) < 1024:  # 1KB mínimo
            validation_error = f"Arquivo muito pequeno: {key} ({head['ContentLength']} bytes)"
    except Exception as e:
        validation_error = f"Falha ao acessar {key}: {str(e)}"

    if validation_error:
        logging.error(f"❌ {validation_error}")
        return []

    # 📥 Download e processamento
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
        try:
            s3_client.download_file(bucket, key, tmp_file.name)
            if os.path.getsize(tmp_file.name) == 0:
                raise ValueError(f"Arquivo vazio após download: {key}")

            # 📄 Carregamento do PDF
            loader = PyPDFLoader(tmp_file.name)
            pages = loader.load()
            full_text = "\n".join([page.page_content for page in pages])

            # 🔍 Processamento do texto e metadados
            processor = LegalTextProcessor()
            extractor = LegalMetadataExtractor()

            metadata = extractor.extract_from_text(full_text)
            documents = processor.process(full_text)

            path_meta = _extract_path_metadata(key)

            for doc in documents:
                doc.metadata.update({
                    **metadata,
                    "source": key,
                    "s3_uri": f"s3://{bucket}/{key}",
                    "processing_timestamp": datetime.utcnow().isoformat() + "Z",
                    "timestamp": datetime.utcnow().isoformat(),
                    "document_language": "pt-BR",
                    "embedding_ready": False,
                    **path_meta,
                    "s3_etag": head.get('ETag', '').strip('"'),
                    "s3_last_modified": head.get('LastModified', '').isoformat()
                })

            logging.info(f"✅ {key} → {len(documents)} chunks")
            return documents

        except Exception as e:
            logging.error(f"🚨 Erro processando {key}: {str(e)}")
            return []


def list_pdfs_in_bucket(bucket: str, prefix: str = "juridicos/") -> List[Dict]:
    """Lista todos os PDFs no bucket com paginação"""
    pdfs = []
    paginator = s3_client.get_paginator('list_objects_v2')

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            if obj['Key'].lower().endswith('.pdf'):
                pdfs.append({
                    'bucket': bucket,
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })
    return pdfs


def process_all_pdfs_in_bucket(bucket: str) -> List[Document]:
    """Processa todos os PDFs encontrados no bucket de forma recursiva"""
    all_docs = []
    pdf_files = list_pdfs_in_bucket(bucket)

    for pdf in pdf_files:
        try:
            docs = process_pdf_from_s3(pdf['bucket'], pdf['key'])
            all_docs.extend(docs)
            logging.info(f"✅ {pdf['key']} → {len(docs)} chunks")
        except Exception as e:
            logging.error(f"🚨 Erro processando {pdf['key']}: {str(e)}")

    logging.info(
        f"📚 Total processado: {len(all_docs)} chunks de {len(pdf_files)} PDFs")
    return all_docs
