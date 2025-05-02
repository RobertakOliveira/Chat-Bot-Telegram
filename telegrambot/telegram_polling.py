import os
import requests
import telegram
from telegram import Update
from telegram.constants import ChatAction
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("init_chroma")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Sou o chatbot do grupo 3. Tenho acesso a uma série de documentos jurídicos e posso lhe responder quaisquer dúvidas acerca de seu conteúdo. Como posso lhe ajudar hoje?")

#fazer um request para o flask
async def fazer_request_flask(mensagem, chat_id):
    url = "http://host.docker.internal:80/query"  # URL do endpoint Flask
    payload = {"query": mensagem, "chat_id": chat_id}  # Payload com a mensagem
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()  # Retorna a resposta JSON do Flask
        else:
            return {"error": "Erro ao processar a solicitação."}
    except Exception as e:
        logger.error(f'Não foi possível realizar requisição à API: {e}')
        return {"response": "Perdão! Houve um erro ao processar a sua solicitação. A API que me providencia respostas pode estar temporariamente fora do ar. Por favor, tente novamente em alguns intantes."}


# Qualquer mensagem de texto
async def responder_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_chat_action(ChatAction.TYPING)
    #await app.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    await update.message.reply_text("Só um momento enquanto busco informações...")

    #fazer um request para o flask
    resposta = await fazer_request_flask(update.message.text, update.message.chat_id)
    resposta_tratada = resposta.get("response", "Nenhuma resposta encontrada.")

    await update.message.reply_text(resposta_tratada)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_texto))

    print("Iniciando polling...")
    app.run_polling()
