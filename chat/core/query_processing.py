# chat/core/query_processing.py
import json
import re
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from botocore.exceptions import ClientError

from chat.core.query_embeddings import get_query_embedding
from chat.utils.logger import get_logger
from chat.utils.aws_clients import bedrock_runtime
from chat.utils.config import bedrock_config

logger = get_logger(
    "Processamento de Consultas Jurídicas com as Perguntas do Usuário")


@dataclass
class UserSession:
    """Contêiner para manter o estado isolado por usuário"""
    user_id: str
    chat_history: List[Dict] = field(default_factory=list)

    def add_message(self, message: str, is_user: bool = True) -> None:
        """Adiciona mensagem ao histórico mantendo contexto"""
        msg_type = "user" if is_user else "assistant"
        self.chat_history = self.chat_history or []
        self.chat_history.append({
            "role": msg_type,
            "message": message[:2000]
        })  # Limita tamanho

        # Adiciona log para verificação
        logger.debug(
            f"1 - Mensagem adicionada ao histórico: {message[:100]}...")

    def get_history(self) -> List[Dict]:
        """Retorna o histórico de mensagens"""
        return self.chat_history

    def get_history_text(self) -> str:
        """Retorna o histórico de mensagens como uma string de texto"""
        history_text = ""
        for message in self.chat_history:
            role = message['role']
            msg = message['message']
            history_text += f"{role.capitalize()}: {msg}\n"
        return history_text


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
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": [{"text": msg["message"]}]
            }
            for msg in session.chat_history
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

        logger.debug(
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
    system_msg = """
    Você é um classificador especializado em documentos judiciais. 
    Sua tarefa é classificar perguntas em tipo documental e intenção.
    
    Para cada pergunta, siga este processo de raciocínio:
    
    1. ANÁLISE INICIAL: Identifique o tema principal da pergunta e seus elementos-chave
    2. CLASSIFICAÇÃO DO TIPO DOCUMENTAL: Determine qual tipo de documento judicial é mais relevante
    3. CLASSIFICAÇÃO DA INTENÇÃO: Identifique o objetivo principal do usuário ao fazer a pergunta
    4. VERIFICAÇÃO: Revise se a classificação atende aos critérios definidos
    
    TIPOS DE DOCUMENTO PERMITIDOS:
    - Decisao Admissibilidade: Avalia requisitos para processamento de recursos em instâncias superiores
    - Acordao Recorrido: Decisão colegiada que está sendo contestada em recurso
    - Agravo: Recurso contra decisões interlocutórias que não encerram o processo
    - Recurso Extraordinario: Recurso ao STF por violação direta à Constituição Federal
    - Acordao Embargos: Decisão sobre embargos de declaração para corrigir omissões/contradições
    - 'outro': Quando não se encaixa em nenhuma das categorias acima
    
    INTENÇÕES PERMITIDAS:
    - 'buscar_info': Usuário quer obter informações específicas ou gerais
    - 'comparar': Usuário quer comparar elementos, decisões ou entendimentos
    - 'esclarecer_duvida': Usuário tem dúvida conceitual ou procedimental
    - 'outro': Quando a intenção não se encaixa nas categorias acima
    
    Exemplos de classificação:
    
    [EXEMPLO 1]
    Pergunta: "Como funciona o prazo para interpor agravo contra decisão que negou seguimento ao recurso?"
    Análise: A pergunta trata de prazos processuais e menciona especificamente "agravo"
    Tipo Documental: Identifica-se claramente como relacionado a "Agravo"
    Intenção: O usuário busca informações sobre procedimentos, então é "buscar_info"
    Classificação Final: {"doc_type": "Agravo", "intent": "buscar_info"}
    
    [EXEMPLO 2]
    Pergunta: "Qual a diferença entre os requisitos de admissibilidade de recursos extraordinários e especiais?"
    Análise: A pergunta aborda requisitos de admissibilidade e menciona recursos extraordinários
    Tipo Documental: Relaciona-se principalmente com "Decisao Admissibilidade", mas também com "Recurso Extraordinario"
    Intenção: O usuário quer comparar diferentes tipos de requisitos, então é "comparar"
    Classificação Final: {"doc_type": "Decisao Admissibilidade", "intent": "comparar"}
    
    [EXEMPLO 3]
    Pergunta: "Por que meu recurso extraordinário não foi admitido pelo STF?"
    Análise: A pergunta relaciona-se a admissibilidade de recurso extraordinário
    Tipo Documental: Claramente vinculado a "Recurso Extraordinario" e sua admissibilidade
    Intenção: O usuário tem dúvida sobre razões de inadmissão, então é "esclarecer_duvida"
    Classificação Final: {"doc_type": "Recurso Extraordinario", "intent": "esclarecer_duvida"}
    
    [EXEMPLO 4]
    Pergunta: "No acórdão dos embargos, o tribunal considerou todos os argumentos levantados?"
    Análise: A pergunta menciona explicitamente "acórdão dos embargos"
    Tipo Documental: Diretamente relacionado a "Acordao Embargos"
    Intenção: O usuário busca informação sobre o conteúdo de uma decisão, então é "buscar_info"
    Classificação Final: {"doc_type": "Acordao Embargos", "intent": "buscar_info"}
    
    Responda APENAS com um JSON válido, no formato:
    {
        "doc_type": "...",
        "intent": "..."
    }
    """

    try:
        # Remove o 'prompt' da chamada, pois agora só usamos 'messages'
        response = invoke_nova_pro_rag_preprocess(
            prompt=query,  # Apenas a pergunta do usuário
            session=session,
            system_message=system_msg  # Todas as regras de classificação
        )

        json_match = re.search(r'\{[\s\S]*?\}', response.strip())
        if json_match:
            result = json.loads(json_match.group())
            return {
                "doc_type": result.get("doc_type", "outro"),
                "intent": result.get("intent", "outro")
            }
        return {"doc_type": "outro", "intent": "outro"}
    except Exception as e:
        logger.error(f"⚠️ Falha na classificação: {str(e)}", exc_info=True)
        return {"doc_type": "outro", "intent": "outro"}


def refine_query(query: str, doc_type: str, session: UserSession) -> str:
    """Refina a pergunta para busca jurídica."""
    if doc_type == "outro":
        return query

    system_msg = f"""
    Você é um especialista em reformulação de consultas jurídicas. Sua tarefa é adaptar perguntas para busca eficiente em documentos do tipo '{doc_type}' armazenados em ChromaDB.

    Para cada consulta, siga este processo de raciocínio:

    1. ANÁLISE INICIAL: Identifique o núcleo da pergunta e o objetivo do usuário
    2. IDENTIFICAÇÃO DE ENTIDADES: Verifique se a pergunta menciona pessoas físicas ou jurídicas
    3. TERMOS TÉCNICOS: Determine quais termos jurídicos específicos devem ser adicionados
    4. REFORMULAÇÃO: Reescreva a pergunta integrando os termos técnicos mantendo o significado original
    5. VERIFICAÇÃO: Confirme que a reformulação é concisa (máx. 2 linhas) e mantém o núcleo da pergunta

    Para consultas sobre PESSOAS mencionadas nos documentos:
    - Mantenha o nome completo da pessoa na reformulação
    - Adicione qualificadores relevantes (ex: "como parte", "como julgador", "como advogado")
    - Conecte a pessoa ao contexto jurídico apropriado para o tipo de documento

    Dependendo do tipo de documento, inclua os seguintes termos técnicos específicos:

    - Recurso Extraordinário: "STF", "Constituição Federal", "violação direta", "repercussão geral"
    - Agravo: "recurso interlocutório", "art. 1.015 do CPC", "decisão saneadora", "efeito suspensivo"
    - Decisão Admissibilidade: "pressupostos de admissibilidade", "requisitos intrínsecos/extrínsecos", "juízo de admissibilidade"

    Exemplos de reformulações bem-sucedidas:

    [EXEMPLO 1 - Consulta geral]
    Original: "Como recorrer de decisão liminar?"
    Análise: A pergunta trata sobre procedimento recursal contra decisão provisória
    Termos técnicos: Para documento tipo 'Agravo', incluir "recurso interlocutório" e "art. 1.015 do CPC"
    Reformulação: "Procedimento para interposição de recurso interlocutório contra decisão liminar conforme art. 1.015 do CPC"

    [EXEMPLO 2 - Consulta sobre pessoa]
    Original: "Quais processos envolvem João Silva?"
    Análise: Pergunta sobre documentos relacionados a uma pessoa específica
    Identificação: "João Silva" é o nome de uma pessoa física
    Termos técnicos: Conectar a pessoa ao contexto jurídico apropriado
    Reformulação: "Processos com João Silva como parte, advogado ou julgador relacionados a recurso interlocutório ou decisão saneadora"

    [EXEMPLO 3 - Consulta sobre pessoa em contexto específico]
    Original: "O ministro Roberto Barroso votou em qual sentido no caso X?"
    Análise: Pergunta sobre posicionamento de um julgador específico
    Identificação: "Roberto Barroso" é um ministro do STF
    Termos técnicos: Para documento tipo 'Recurso Extraordinário', incluir "voto", "STF" e "Constituição Federal"
    Reformulação: "Voto do ministro Roberto Barroso no STF referente à violação direta da Constituição Federal no caso X"

    Formato de saída: Apenas a pergunta reformulada, sem prefixos, comentários ou explicações adicionais.
    """

    prompt = f"Pergunta original a ser refinada: {query}"

    try:
        refined_text = invoke_nova_pro_rag_preprocess(
            prompt=prompt,  # Apenas a pergunta original
            session=session,
            system_message=system_msg  # Todas as regras de refinamento
        )
        return refined_text.strip() if refined_text else query
    except Exception:
        logger.info(" ⚠️ Falha no refinamento, retornando query original")
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
        # 1. Classificação
        classification = classify_query(user_query, session)

        # 2. Refinamento condicional
        doc_type = classification["doc_type"]
        refined_query = refine_query(user_query, doc_type, session)

        # 3. Preparar saída
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
# Isso pode ser útil para capturar uma gama mais ampla de documentos que podem ser relevantes para a consulta do usuário.
# No entanto, é importante garantir que a busca ainda seja eficiente e relevante, mesmo sem um filtro específico. Isso pode ser feito ajustando os parâmetros de busca ou utilizando técnicas de recuperação de informações que considerem a similaridade semântica.
