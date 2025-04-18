from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from config import API_SECRET_KEY, TELEGRAM_BOT_TOKEN
from dotenv import load_dotenv
from fastapi.security import APIKeyHeader
from typing import Optional
import httpx
import logging
import psutil

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuração Inicial ---
load_dotenv()

app = FastAPI(
    title="Chatbot Jurídico API",
    version="1.0.0",
    description="API para processamento de perguntas jurídicas com integração RAG e Telegram"
)

# --- Segurança por API Key ---
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# --- Modelos de Dados ---
class Question(BaseModel):
    text: str
    chat_id: Optional[str] = None
    context: Optional[dict] = None

# --- Endpoints ---
@app.get("/instance-health")
async def instance_health():
    return {
        "status": "healthy",
        "service": "chatbot-api",
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent
    }

@app.post("/ask", dependencies=[Depends(get_api_key)])
async def ask_question(question: Question):
    try:
        # Simulação de resposta do sistema RAG
        rag_response = {
            "answer": "Resposta simulada - sistema RAG em desenvolvimento",
            "sources": ["Lei 1234/56", "Jurisprudência XYZ"],
            "confidence": 0.85
        }

        response = {
            "question": question.text,
            **rag_response
        }

         # ✅ LOG por usuário (para CloudWatch)
        logger.info({
            "chat_id": question.chat_id,
            "question": question.text,
            "answer": rag_response["answer"],
            "confidence": rag_response["confidence"],
            "sources": rag_response["sources"]
        })

        if question.chat_id:
            await telegram_send_message(question.chat_id, rag_response["answer"])

        return response

    except Exception as e:
        logger.exception("Erro ao processar pergunta")
        raise HTTPException(status_code=500, detail=str(e))

# --- Funções Auxiliares ---
async def telegram_send_message(chat_id: str, text: str):
    bot_token = TELEGRAM_BOT_TOKEN
    if not bot_token:
        raise HTTPException(status_code=500, detail="Telegram bot token not configured")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"   # URL da API do Telegram para enviar mensagens
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except Exception as e:
        logger.exception("Erro ao enviar mensagem para Telegram")
        raise HTTPException(status_code=500, detail=f"Telegram API error: {str(e)}")
