from chat.core.query_processing import preprocess_query, UserSession
from chat.scripts.rag_flow import RAGFlow 
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
    case_id: Optional[str] = None # ID do caso para o RAG (opcional)

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
        # --- 1. Sessão do usuário (controla histórico, contexto, etc) ---
        if chat_id in user_sessions:
            session = user_sessions[chat_id]
        else:
            # Se não tiver sessão ainda, cria uma nova e guarda no dicionário
            session = UserSession(user_id=str(chat_id))
            user_sessions[chat_id] = session
        
        # --- 2. Pipeline principal: chama o motor RAG para processar a pergunta ---
        rag_engine = RAGFlow() # Instancia o motor que conecta embeddings + modelo LLM
        rag_response = rag_engine.execute(
            query=question.text, # Passa a pergunta original
            user_session=session, # Leva junto a sessão (pra usar dados como histórico ou cache)
        )

        # --- 3. Loga tudo: quem perguntou, o quê, e a resposta gerada ---
        logger.info({
            "chat_id": question.chat_id,
            "question": question.text,
            "answer": rag_response["answer"],
            "metadata": rag_response.get("metadata", {})
        })

        # --- 4. Retorna a resposta final para o frontend / Telegram / etc ---
        return rag_response  # Retorna a resposta para o cliente

    except Exception as e:
        logger.exception("Erro ao processar pergunta") # Em caso de erro, registra exceção completa no log
        raise HTTPException(status_code=500, detail=str(e)) # Retorna erro 500 (Internal Server Error) com detalhes
    
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
