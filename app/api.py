from chat.core.query_processing import preprocess_query, UserSession
from app.config import API_SECRET_KEY, TELEGRAM_BOT_TOKEN  # Configurações sensíveis
from fastapi import FastAPI, HTTPException, Depends  # Framework para criar a API
from fastapi.security import APIKeyHeader  # Para autenticação via header
from pydantic import BaseModel  # Para validação de dados com modelos
from typing import Optional  # Para tipagem de campos opcionais
import httpx  # Cliente HTTP assíncrono para chamadas externas
import psutil  # Para monitoramento de sistema (CPU, memória)
# import logging  # Para registro de logs
from chat.utils.logger import get_logger  # Logger personalizado

logger = get_logger("chatbot_api")  # Logger para a API
# --- Importações para o RAG e processamento de consultas --- #
# Importe a função preprocess_query
# Função e classe para processamento de consultas

# # --- Configuração de Logging ---
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# Cria a aplicação FastAPI com metadados para documentação
app = FastAPI(
    title="Chatbot Jurídico API",  # Nome da API
    version="1.0.0",  # Versão atual
    description="API para processamento de perguntas jurídicas com integração RAG e Telegram"  # Descrição
)

# Configuração do sistema de autenticação por API Key
API_KEY_NAME = "X-API-KEY"  # Nome do header que conterá a chave
api_key_header = APIKeyHeader(
    name=API_KEY_NAME, auto_error=False)  # Configura o header

# Função para validar a API Key recebida no header


async def get_api_key(api_key: Optional[str] = Depends(api_key_header)):
    # Compara a chave recebida com a chave armazenada nas variáveis de ambiente, se não for válida, retorna erro 403 (Forbidden)
    if api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Modelo Pydantic para validação do payload de perguntas


class Question(BaseModel):
    text: str  # Texto da pergunta (campo obrigatório)
    chat_id: Optional[str] = None  # ID do chat no Telegram (opcional)
    context: Optional[dict] = None  # Contexto adicional para o RAG (opcional)

# Endpoint para verificação do status da instância


@app.get("/instance-health")
async def instance_health():
    """
    Endpoint de health check que retorna o status atual da instância
    e informações de utilização de recursos
    """
    return {
        "status": "healthy",  # Status geral do serviço
        "service": "chatbot-api",  # Nome do serviço
        "cpu": psutil.cpu_percent(),  # % de uso da CPU
        "memory": psutil.virtual_memory().percent  # % de uso da memória
    }

# Endpoint principal para envio de perguntas

# Dicionário para armazenar sessões de usuários (chat_id -> UserSession)
user_sessions = {}


@app.post("/ask", dependencies=[Depends(get_api_key)])  # Protegido por API Key
async def ask_question(question: Question):
    """
    Processa perguntas jurídicas e retorna respostas usando sistema RAG.
    Opcionalmente envia a resposta para o Telegram se chat_id for fornecido.
    """
    chat_id = question.chat_id  # ID do chat (se fornecido)
    try:

        # TODO: Criar uma sessão de usuário com o chat_id (caso existam múltiplos usuários)
        # 1. Tentar recuperar a sessão existente
        if chat_id in user_sessions:
            session = user_sessions[chat_id]
        else:
            # 2. Se não existir, criar uma nova sessão
            # Certifique-se de que user_id seja string
            session = UserSession(user_id=str(chat_id))
            user_sessions[chat_id] = session

        # Adiciona a nova mensagem do usuário ao histórico
        session.add_message(question.text)
        # Log detalhado da mensagem do usuário
        logger.info(
            f"Histórico da sessão antes do pré-processamento: {session.chat_history}")

        # TODO: Chamar a função preprocess_query para processar a consulta
        refined_query = preprocess_query(question.text, session)
        refined_query_text = refined_query.get(
            'refined_query', 'Não foi possível obter o histórico das perguntas refinada.')

        # Log detalhado do resultado do pré-processamento
        logger.info(f"Resultado do pré-processamento: {refined_query_text}")

        # TODO: Recuperar a consulta refinada e o embedding gerado
        # refined_query = result['refined_query']
        # embedding = result['embedding']
        # doc_type = result['doc_type']
        # intent = result['intent']
        # search_filters = result['search_filters']

        # Chama a função do RAG com os parâmetros que você já tem
        # rag_response = generate_rag_response(refined_query)

        # SIMULAÇÃO: Resposta do sistema RAG (em desenvolvimento)
        rag_response = {
            "answer": "Resposta simulada - sistema RAG em desenvolvimento",
            # Fontes da resposta
            "sources": ["Lei 1234/56", "Jurisprudência XYZ"],
            "confidence": 0.85  # Nível de confiança da resposta (0-1)
        }

        # Constrói a resposta final combinando pergunta e resposta RAG
        response = {
            "question": question.text,  # Repete a pergunta recebida
            "refined_query": refined_query,  # Exibe a pergunta refinada para debug
            **rag_response  # Inclui todos os campos da resposta RAG
        }

        # Registra a interação completa no log
        logger.info({
            "chat_id": question.chat_id,  # ID do chat (se existir)
            "question": question.text,  # Texto da pergunta
            "answer": rag_response["answer"],  # Resposta gerada
            "confidence": rag_response["confidence"],  # Nível de confiança
            "sources": rag_response["sources"]  # Fontes utilizadas
        })

        # Se existir chat_id, envia resposta para o Telegram (código comentado)
        # if question.chat_id:
        #     await telegram_send_message(question.chat_id, rag_response["answer"])
        if question.chat_id:
            # Envia a pergunta refinada
            refined_query_text = refined_query.get(
                'refined_query', 'Não foi possível obter a consulta refinada.')
            await telegram_send_message(question.chat_id, refined_query_text)
        return response  # Retorna a resposta para o cliente

    except Exception as e:
        # Em caso de erro, registra exceção completa no log
        logger.exception("Erro ao processar pergunta")
        # Retorna erro 500 (Internal Server Error) com detalhes
        raise HTTPException(status_code=500, detail=str(e))

# Função para enviar mensagens para o Telegram


async def telegram_send_message(chat_id: str, text: str):
    """
    Envia mensagens para um chat específico no Telegram via bot.
    Args:
        chat_id: ID do chat no Telegram
        text: Mensagem a ser enviada
    """
    # Obtém o token do bot das variáveis de ambiente
    bot_token = TELEGRAM_BOT_TOKEN
    if not bot_token:
        # Se não estiver configurado, retorna erro 500
        raise HTTPException(
            status_code=500, detail="Telegram bot token not configured")

    # URL da API do Telegram para envio de mensagens
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Payload com os dados da mensagem
    payload = {
        "chat_id": chat_id,  # Destinatário
        "text": text,  # Texto da mensagem
        "parse_mode": "Markdown"  # Formatação Markdown
    }

    try:
        # Cria cliente HTTP assíncrono e envia a mensagem
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()  # Levanta exceção para respostas de erro
    except Exception as e:
        # Em caso de erro, registra exceção completa
        logger.exception("Erro ao enviar mensagem para Telegram")
        # Retorna erro 500 com detalhes
        raise HTTPException(
            status_code=500, detail=f"Telegram API error: {str(e)}")


# Instruções para rodar localmente: (diretorio raiz)
# uvicorn app.api:app --reload


# --- Bot em thread paralela ---
# def start_bot():
   # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # run_bot()

# @app.on_event("startup")
# def on_startup():
   # threading.Thread(target=start_bot, daemon=True).start()
