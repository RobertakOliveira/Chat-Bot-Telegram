# chat/core/query_processing.py

# TODO: Integração com o RAG
# ------------------------------------------------------------
# 1. Saída do pré-processamento agora inclui:
#    - 'document_type': tipo de documento detectado (ACORDAO_RECORRIDO, EMBARGOS, etc.)
#    - Demais campos mantidos (processed_query, intent, embedding)
#
# 2. Uso recomendado no RAG:
#    results = chroma_collection.query(
#        query_embeddings=[processed["embedding"]],
#        where={"document_type": processed["document_type"]}  # Filtro otimizado
#    )
# ------------------------------------------------------------


import re
from typing import Dict
from chat.core.query_embeddings import get_query_embedding
from chat.utils.legal_terms import detect_document_type, normalize_legal_terms, detect_legal_intent
from chat.utils.logger import get_logger

logger = get_logger("query_processing")


def preprocess_query(user_query: str, chat_history: list = None) -> Dict:
    """
    Processa a pergunta do usuário antes de enviar ao RAG.

    Args:
        user_query: Pergunta bruta do usuário
        chat_history: Histórico da conversa (opcional para contexto)

    Returns:
        Dict: {
            "status": "success"|"error",
            "original_query": str,
            "processed_query": str,
            "intent": str,
            "document_type": str,
            "search_filters": Dict,  # Filtros prontos para o ChromaDB
            "embedding": list[float],
            "error": Optional[str]
        }"""
    try:
        # 1. Normalização jurídica
        processed_query = normalize_legal_terms(user_query)

        # 2. Análise jurídica
        intent = detect_legal_intent(processed_query)
        doc_type = detect_document_type(processed_query)

        # 3. Preparação de filtros para ChromaDB Define se a query é específica ou ampla
        is_specific = any(
            term in user_query.lower()
            for term in [
                "acórdão recorrido",
                "embargos",
                "agravo de instrumento",
                "recurso extraordinário",
                "admissibilidade"
            ]
        )

        if doc_type:
            if is_specific:
                search_filters = {"doc_type": doc_type}
            else:
                search_filters = {"doc_type": {"$ne": None}}
        else:
            search_filters = {}

        # PODE-SE REFINAR A PERGUNTA APÓS O PRÉ-PROCESSAMENTO: refined_query = refine_query_with_bedrock(processed_query)
        # ASSIM ENTÃO A PERGUNTA REFINADA SERÁ USADA NO CHROMADB: embedding = get_query_embedding(refined_query)

        # 4. Geração de embedding
        embedding = get_query_embedding(processed_query)

        # 5. Estrutura do retorno para ser usado no RAG
        return {
            "status": "success",
            "original_query": user_query,
            # Agora, a consulta é refinada: #  "processed_query": refined_query,
            "processed_query": processed_query,
            "intent": intent,
            "document_type": doc_type,
            "search_filters": search_filters,
            "embedding": embedding,
            "is_general_query": not is_specific,  # Útil para logs
            "error": None
        }

    except Exception as e:
        logger.error(f"Falha no pré-processamento: {str(e)}", extra={
            "original_query": user_query,
            "error": str(e)
        })

        return {
            "status": "error",
            "original_query": user_query,
            "error": str(e),
            **{k: None for k in ["processed_query", "intent", "document_type", "search_filters", "embedding"]}
        }


# Fluxo Atualizado
# Usuário faz uma consulta.
# Pré-processamento: Normalização jurídica, detecção de intenção e tipo de documento.
# Refinamento com Bedrock: Passar a consulta pré-processada para o Bedrock para refinamento.
# Geração de Embedding: Gerar o embedding usando a consulta refinada.
# Busca no ChromaDB: Usar o embedding para buscar documentos relevantes no banco de dados.
