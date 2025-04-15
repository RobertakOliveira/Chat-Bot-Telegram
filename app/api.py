#Este código é uma api desenvolvida com FastAPI, que tem como objetivo processar perguntas jurídicas e enviar respostas via Telegram.
#Ele inclui validação de API Key, integração com um sistema RAG (Recuperação de Resposta Aumentada) e tratamento de erros.
# Importações organizadas por categorias (FastAPI, modelos, HTTP, env, etc.)


from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv 
from fastapi.security import APIKeyHeader
from typing import Optional

# --- Configuração Inicial ---
# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa a aplicação FastAPI com metadados para documentação
app = FastAPI(
    title="Chatbot Jurídico API",
    version="1.0.0",
    description="API para processamento de perguntas jurídicas com integração RAG e Telegram"
)

# --- Configuração de Segurança ---
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: Optional[str] = Depends(api_key_header)):
    """
    Valida a API Key recebida no header contra a chave armazenada no ambiente.
    Caso inválida, retorna erro 403.
    """
    if api_key != os.getenv("API_SECRET_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# --- Modelos de Dados ---
class Question(BaseModel):
    """
    Modelo Pydantic para validação do payload de perguntas.
    Campos:
    - text: O texto da pergunta (obrigatório)
    - chat_id: ID do chat no Telegram (opcional)
    - context: Dicionário para contexto adicional (opcional, usado no RAG)
    """
    text: str
    chat_id: Optional[str] = None
    context: Optional[dict] = None

# --- Endpoints ---
@app.get("/health")
async def health_check():
    """
    Endpoint de health check básico.
    Retorna status do serviço e é útil para monitoramento.
    """
    return {"status": "healthy", "service": "chatbot-api"}

@app.post("/ask", dependencies=[Depends(get_api_key)])
async def ask_question(question: Question):
    """
    Endpoint principal que processa perguntas jurídicas.
    Fluxo:
    1. Recebe a pergunta validada pelo modelo Question
    2. Integra com sistema RAG (a ser implementado)
    3. Se chat_id estiver presente, envia resposta via Telegram
    4. Retorna estrutura padronizada com resposta e metadados
    """
    try:
        # TODO: Integração com RAG será implementada posteriormente
        # Resposta simulada enquanto o RAG está em desenvolvimento
        rag_response = {
            "answer": "Resposta simulada - sistema RAG em desenvolvimento",
            "sources": ["Lei 1234/56", "Jurisprudência XYZ"],
            "confidence": 0.85
        }
        
        # Estrutura de resposta padronizada
        response = {
            "question": question.text,
            **rag_response
        }
        
        # Envia resposta via Telegram se chat_id foi fornecido
        if question.chat_id:
            await telegram_send_message(question.chat_id, rag_response["answer"])
        
        return response
        
    except Exception as e:
        # Tratamento genérico de erros com logging adequado (a ser implementado)
        raise HTTPException(status_code=500, detail=str(e))

# --- Funções de Apoio ---
async def telegram_send_message(chat_id: str, text: str):
    """
    Envia mensagem de forma assíncrona via API do Telegram.
    
    Parâmetros:
    - chat_id: ID do chat/conversa no Telegram
    - text: Mensagem formatada em Markdown a ser enviada
    
    Levanta:
    - HTTPException 500 se o token não estiver configurado ou em caso de falha na API
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise HTTPException(
            status_code=500,
            detail="Telegram bot token not configured"
        )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"  # Permite formatação básica
    }
    
    try:
        # Usa cliente HTTP assíncrono para melhor performance
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Telegram API error: {str(e)}"
        )