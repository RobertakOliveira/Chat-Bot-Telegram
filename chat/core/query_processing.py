# chat/core/query_processing.py
# Garantir que o pré-processamento de cada consulta seja realizado de forma isolada por usuário, para que as informações não se misturem entre os usuários.
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


import json
import re
from dataclasses import dataclass
from typing import Dict, Optional, List
from botocore.exceptions import ClientError

from chat.core.query_embeddings import get_query_embedding
from chat.utils.logger import get_logger
from chat.utils.aws_clients import bedrock_runtime
from chat.utils.config import bedrock_config

logger = get_logger("query_processing")


@dataclass
class UserSession:
    """Contêiner para manter o estado isolado por usuário"""
    user_id: str
    chat_history: List[Dict] = None

    def add_message(self, message: str, is_user: bool = True) -> None:
        """Adiciona mensagem ao histórico mantendo contexto"""
        msg_type = "user" if is_user else "assistant"
        self.chat_history = self.chat_history or []
        self.chat_history.append({
            "type": msg_type,
            "message": message[:2000]
        })  # Limita tamanho


def invoke_nova_pro_rag_preprocess(prompt: str, session: UserSession, system_message: Optional[str] = None) -> str:
    """
    Invoca o Amazon Nova Pro usando a API Converse do Bedrock com todos os parâmetros documentados.

    Args:
        prompt: Texto da consulta do usuário
        session: Sessão contendo histórico de conversa
        system_message: Instruções de sistema opcionais

    Returns:
        str: Resposta textual do modelo

    Configurações padrão:
        - temperature: 0.3 (mais determinístico)
        - topP: 0.9 (amostragem de núcleo)
        - maxTokens: Definido em bedrock_config
        - stopSequences: [] (sem paradas pré-definidas)
        """
    try:
        # 1. Construir o payload específico para o Amazon Nova Pro
        messages = [
            {
                "role": "user" if msg["type"] == "user" else "assistant",
                "content": [{"text": msg["message"]}]
            }
            for msg in (session.chat_history[-3:] if session.chat_history else [])
        ]
        messages.append({
            "role": "user",
            "content": [{"text": prompt}]
        })

        # 2. Configuração de inferência
        inference_config = {
            "maxTokens": bedrock_config.MAX_TOKENS,
            "temperature": 0.3,  # Valor mais baixo para tarefas determinísticas
            "topP": 0.9,        # Amostragem de núcleo padrão
            "stopSequences": [],  # Sem sequências de parada específicas
        }
        # 3.  Preparar payload completo
        converse_params = {
            "modelId": bedrock_config.BEDROCK_QUERY_MODEL_ID,
            "messages": messages,
            "inferenceConfig": inference_config
        }

        # Adicionar system message se fornecida (opcional)
        if system_message:
            converse_params["system"] = [{"text": system_message}]

        logger.info(
            f"Enviando para o Nova Pro: {json.dumps(converse_params, indent=2)}")

        # 4. Chamada à API Converse
        response = bedrock_runtime.converse(**converse_params)

        # 5. Processar resposta
        if not response or "output" not in response:
            raise RuntimeError("Resposta inválida da API")

        response_text = response["output"]["message"]["content"][0]["text"]
        logger.info(
            f"Resposta recebida - Tokens: {response.get('usage', {}).get('outputTokens', 'N/A')}")
        return response_text
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"Erro AWS ({error_code}): {str(e)}", extra={
            "model_id": bedrock_config.BEDROCK_QUERY_MODEL_ID,
            "error_details": e.response['Error']
        })
        raise RuntimeError(
            f"Falha na chamada à API Bedrock: {error_code}") from e

    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        raise RuntimeError("Erro ao processar consulta no Nova Pro") from e


def classify_query(query: str, session: UserSession) -> Dict:
    """Classifica a pergunta em tipo documental e intenção."""
    system_msg = """Você é um classificador especializado em documentos judiciais. 
    Responda APENAS com JSON contendo 'doc_type' e 'intent'."""

    prompt = f"""
    Classifique a pergunta jurídica abaixo APENAS com os valores permitidos:
    1. Tipo de Documento permitidos: Decisao Admissibilidade, Acordao Recorrido, Agravo, Recurso Extraordinario, Acordao Embargos ou 'outro'
    2. Intenções permitidas: 'buscar_info', 'comparar', 'esclarecer_duvida' ou 'outro'.

    Termos jurídicos explicados:
        Agravo: Um recurso utilizado para contestar decisões interlocutórias, ou seja, decisões que não encerram o processo. Exemplo: Quando um juiz nega seguimento a um recurso.
        Decisão de Admissibilidade: A decisão que verifica se um recurso pode ser aceito para ser julgado nas instâncias superiores. Exemplo: Decisão sobre a admissibilidade de um recurso especial no STJ ou STF.
        Acórdão Embargos: Decisão colegiada resultante de embargos de declaração, usados para esclarecer omissões ou contradições nas decisões anteriores.
        Acórdão Recorrido: O acórdão que está sendo contestado em um recurso. Exemplo: Se uma das partes não concorda com a decisão, entra com um recurso.
        Recurso Extraordinário: Recurso que vai ao Supremo Tribunal Federal (STF) quando há violação direta à Constituição. Exemplo: Decisão judicial que fere um direito fundamental.

    Retorne APENAS JSON válido com a estrutura:
        {{
            "doc_type": "...",
            "intent": "..."
        }}
    Pergunta: {query}
    """
    try:
        response = invoke_nova_pro_rag_preprocess(
            prompt, session, system_message=system_msg)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return {
                "doc_type": result.get("doc_type", "outro"),
                "intent": result.get("intent", "outro")
            }
        return {"doc_type": "outro", "intent": "outro"}
    except Exception:
        logger.warning(" ⚠️ Falha na classificação, retornando valores padrão")
        return {"doc_type": "outro", "intent": "outro"}


def refine_query(query: str, doc_type: str, session: UserSession) -> str:
    """Refina a pergunta para busca jurídica."""
    if doc_type == "outro":
        return query

    system_msg = "Você é um assistente para reformulação de consultas jurídicas. Responda APENAS com a pergunta refinada."

    prompt = f"""
    Reformule esta pergunta para busca em documentos jurídicos do tipo '{doc_type}'.
    - Adicione termos técnicos jurídicos
    - Mantenha o significado original
    - Seja conciso
    
    Pergunta original: {query}
    """
    try:
        refined_text = invoke_nova_pro_rag_preprocess(
            prompt, session, system_message=system_msg)
        return refined_text.strip() if refined_text else query
    except Exception:
        logger.warning(" ⚠️ Falha no refinamento, retornando query original")
        return query


def preprocess_query(user_query: str, session: UserSession) -> Dict:
    """
    Fluxo principal de pré-processamento para RAG

    Processos:
    1. Classificação da pergunta
    2. Refinamento condicional
    3. Geração de embedding

    Args:
        user_query (str): Pergunta bruta do usuário
        chat_history (list): Histórico da conversa (opcional para contexto)

    Returns:
        - dict: Resposta do modelo com a classificação da pergunta e geração de embedding."""
    try:

        # Registrar a nova mensagem
        session.add_message(user_query)

        # 1. Classificação
        classification = classify_query(user_query, session)

        # 2. Refinamento condicional
        doc_type = classification["doc_type"]
        refined_query = refine_query(user_query, doc_type, session)

        # 5. Preparar saída
        return {
            "status": "success",
            "original_query": user_query,
            "refined_query": refined_query,
            "embedding": get_query_embedding(refined_query),
            "doc_type": doc_type,
            "intent":  classification["intent"],
            "search_filters": {"doc_type": doc_type} if doc_type != "outro" else None
        }

    except Exception as e:
        logger.error(
            f"Erro no pré-processamento: {str(e)}", extra={"query": user_query})
        return {
            "status": "error",
            "original_query": user_query,
            "error": str(e),
            "search_filters": None
        }


# Fluxo Atualizado
# Usuário faz uma consulta.
# Pré-processamento: Normalização jurídica, detecção de intenção e tipo de documento.
# Refinamento com Bedrock: Passar a consulta pré-processada para o Bedrock para refinamento.
# Geração de Embedding: Gerar o embedding usando a consulta refinada.

# Ponto Importante
# Caso o doc_type seja "outro", a busca no ChromaDB pode ser realizada sem filtro ou com um filtro mais amplo, dependendo de como você quer estruturar essa parte do código. Isso permite que a consulta seja feita de forma mais flexível, sem restrições quando o tipo de documento não é claramente identificado.

if __name__ == "__main__":
    # Configuração inicial de teste
    print("🐞 Modo de Depuração Ativo - Amazon Nova Pro\n")

    # Inicializa sessão de teste
    test_session = UserSession(user_id="test_nova_pro")

    # Teste 1: Pergunta específica sobre Agravo
    pergunta1 = "Quais os prazos para interpor agravo?"
    print(f"\n🔵 TESTE 1: {pergunta1}")
    resultado1 = preprocess_query(pergunta1, test_session)
    print(
        f"Classificação: {resultado1['doc_type']} | Intenção: {resultado1['intent']}")
    print(f"Refinada: {resultado1['refined_query']}")

    # Teste 2: Pergunta sobre Recurso Extraordinário
    pergunta2 = "Como funciona um recurso extraordinário no STF?"
    print(f"\n🟡 TESTE 2: {pergunta2}")
    resultado2 = preprocess_query(pergunta2, test_session)
    print(
        f"Classificação: {resultado2['doc_type']} | Intenção: {resultado2['intent']}")

    # Teste 3: Com histórico
    test_session.add_message("O que é uma decisão de admissibilidade?")
    test_session.add_message(
        "É a decisão que analisa se um recurso pode ser julgado", False)
    pergunta3 = "Quais os critérios para essa decisão?"
    print(f"\n🟣 TESTE 3 (com histórico): {pergunta3}")
    resultado3 = preprocess_query(pergunta3, test_session)
    print(f"Classificação: {resultado3['doc_type']}")

# Navegue até a pasta raiz e execute:
#     python -m chat.core.query_processing
