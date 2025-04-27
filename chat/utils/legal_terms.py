# chat/utils/legal_terms.py
import re
from typing import Dict, List
from functools import lru_cache


# 1. Dados estáticos
LEGAL_NORMALIZATION_MAP = {
    # Leis e códigos (com variações comuns)
    r'\bclt\b': 'Consolidação das Leis do Trabalho',
    r'\bcpc\b': 'Código de Processo Civil',
    r'\bcpp\b': 'Código de Processo Penal',
    r'\bcp\b': 'Código Penal',
    r'\bcdc\b': 'Código de Defesa do Consumidor',
    r'\bcf\b': 'Constituição Federal',

    # Tribunais (com siglas e nomes populares)
    r'\bstf\b': 'Supremo Tribunal Federal',
    r'\bstj\b': 'Superior Tribunal de Justiça',
    r'\btst\b': 'Tribunal Superior do Trabalho',
    r'\btr[ft]\b': 'Tribunal Regional',  # Captura TRF e TRT
    r'\btj\b': 'Tribunal de Justiça',

    # Estrutura legal (com variações)
    r'\bart\.?\b': 'artigo',
    r'\bparágrafo único\b': '§ único',
    r'\bpar[áa]gr[af]\.?\b': 'parágrafo',
    r'\binc[is]\.?\b': 'inciso',
    r'\bal[íi]n\.?\b': 'alínea',
    r'\bcap[íi]t\.?\b': 'capítulo',
}

LEGAL_INTENT_KEYWORDS = {
    "ARTICLE": [
        "artigo", "lei n°", "lei nº", "art\\.", "parágrafo",
        "inciso", "alínea", "caput", "redação"
    ],
    "JURISPRUDENCE": [
        "jurisprudência", "decisão", "acórdão", "precedente",
        "entendimento", "súmula", "repercussão geral"
    ],
    "DOCTRINE": [
        "doutrina", "teoria", "conceito", "entender",
        "explicar", "interpretação", "fundamento"
    ],
    "PROCEDURE": [
        "prazo", "processo", "petição", "recurso",
        "ajuizar", "protocolo", "andamento"
    ],
    "DEFINITION": [
        "o que é", "definição", "significado",
        "conceituar", "como se define"
    ],
}

# 2. Document types com ordem de prioridade baseada no volume de arquivos
DOCUMENT_TYPES = {
    # Mapeamento completo baseado nos metadados existentes
    "Acordao Recorrido": [
        "acórdão recorrido", "ac.rec.", "decisão recorrida",
        "fundamentos do acórdão", "acordão condenatório"
    ],
    "Acordao Embargos": [
        "embargos de declaração", "embargos infringentes",
        "cabimento de embargos", "opostos embargos", "emb."
    ],
    "Recurso Extraordinario": [
        "recurso extraordinário", "art. 102", "rext",
        "fundamentação do re", "perante o stf"
    ],
    "Decisao Admissibilidade": [
        "admissibilidade", "pressupostos recursais",
        "requisitos de admissão", "art. 301 cpc"
    ],
    "Agravo": [
        "agravo de instrumento", "prazo para agravo",
        "cabimento do agravo", "art. 1.015", "ai n°"
    ]
}
# 3. Cache otimizado
DOC_TYPE_KEYWORDS_CACHE = [
    (doc_type, keyword)
    for doc_type, keywords in DOCUMENT_TYPES.items()
    for keyword in keywords
]

# 2. Função com cache para buscas frequentes


@lru_cache(maxsize=2048)  # Cache para consultas únicas
def _contains_keyword_cached(query: str, keyword: str) -> bool:
    """Verifica se a keyword está na query (com cache)."""
    try:
        return f" {keyword} " in f" {query} "
    except Exception as e:
        print(f"Falha no cache: {str(e)}")
        return False

# 4. Versão otimizada da detect_document_type


def detect_document_type(query: str) -> str:
    """Detecta o tipo de documento com cache de keywords."""
    query_lower = query.lower()

    # Verificação prioritária (sem cache)
    if "embargos de declaração" in query_lower:
        return "Acordao Embargos"
    if "acórdão recorrido" in query_lower:
        return "Acordao Recorrido"
    if "agravo de instrumento" in query_lower:
        return "Agravo"

    # Busca com cache
    for doc_type, keyword in DOC_TYPE_KEYWORDS_CACHE:
        if _contains_keyword_cached(query_lower, keyword):
            return doc_type

    # Fallback inteligente
    if "como contestar" in query_lower or "fundamentos do" in query_lower:
        return "Acordao Recorrido"
    if "pressupostos" in query_lower or "requisitos" in query_lower:
        return "Decisao Admissibilidade"

    return "Acordao Recorrido"


def normalize_legal_terms(query: str) -> str:
    """
    Normaliza termos jurídicos em uma consulta, padronizando abreviações e expressões.

    Args:
        query: Texto da pergunta do usuário

    Returns:
        str: Consulta com termos jurídicos padronizados

    Examples:
        >>> normalize_legal_terms("Art. 483 da CLT")
        "artigo 483 da Consolidação das Leis do Trabalho"
    """
    for pattern, replacement in LEGAL_NORMALIZATION_MAP.items():
        query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)

    # Normaliza citações de artigos (Art. 12 → artigo 12)
    query = re.sub(r'(?i)art\.?\s*(\d+)', r'artigo \1', query)

    # Padroniza referências a leis (Lei 13.467/17 → Lei nº 13.467/2017)
    query = re.sub(
        r'(?i)lei\s*(\d+)\.?(\d+)\/?(\d{2})?',
        r'Lei nº \1.\2/\3',
        query
    )

    return query.strip()


def detect_legal_intent(query: str) -> str:
    """
    Identifica a intenção jurídica por trás da pergunta.

    Args:
        query: Texto da pergunta já normalizado

    Returns:
        str: Intenção detectada (ARTICLE, JURISPRUDENCE, etc.)

    Examples:
        >>> detect_legal_intent("Há súmula sobre o tema?")
        "JURISPRUDENCE"
    """
    query = query.lower()

    # Verifica definições primeiro (para evitar conflitos)
    if any(keyword in query for keyword in LEGAL_INTENT_KEYWORDS["DEFINITION"]):
        return "DEFINITION"

    for intent, keywords in LEGAL_INTENT_KEYWORDS.items():
        if any(
            re.search(rf'\b{re.escape(keyword)}\b', query)
            for keyword in keywords
        ):
            return intent

    return "GENERAL"
