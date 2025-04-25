from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp
import sys
from app.config import API_SECRET_KEY, TELEGRAM_BOT_TOKEN, API_URL
import logging


# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Handlers de comandos e mensagens ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Comando /start recebido do chat_id: {update.effective_chat.id}")
    await update.message.reply_text("👋 Olá! Envie sua dúvida jurídica.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = str(update.effective_chat.id)
    
    logger.info(f"Mensagem recebida - Chat ID: {chat_id}, Mensagem: {user_message}")

    if user_message == "/start":
        await update.message.reply_text("Olá! Envie sua dúvida jurídica.")
        return

    payload = {
        "text": user_message,
        "chat_id": chat_id
    }

    headers = {
        "X-API-KEY": API_SECRET_KEY
    }

    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Enviando para API - Chat ID: {chat_id}, Mensagem: {user_message}")
            async with session.post(API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Resposta da API recebida - Chat ID: {chat_id}, Resposta: {data['answer']}")
                    await update.message.reply_text(data["answer"])
                else:
                    error_msg = f"Erro na API - Status: {response.status}"
                    logger.error(error_msg)
                    await update.message.reply_text(
                        "⚠️ Ops! Não consegui entender sua pergunta agora.\nTente novamente mais tarde."
                    )
        except Exception as e:
            logger.error(f"Erro de conexão com a API - Chat ID: {chat_id}, Erro: {str(e)}")
            await update.message.reply_text(f"❌ Erro de conexão com a API.\nDetalhes: {str(e)}")

# --- Handler para mensagens inválidas (mídia, stickers etc) ---
async def handle_media_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Mídia não suportada recebida - Chat ID: {update.effective_chat.id}")
    await update.message.reply_text(
        "⚠️ Este bot só aceita mensagens de texto.\n\n"
        "📝 Envie sua dúvida jurídica:"
    )

# --- Função principal do bot ---
def run_bot():
    if not TELEGRAM_BOT_TOKEN or not API_URL or not API_SECRET_KEY:
        logger.critical("Variáveis de ambiente não configuradas corretamente")
        sys.exit(1)

    logger.info("✅ Bot do Telegram iniciando...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registra os handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(~filters.TEXT, handle_media_error))

    # Inicia o bot
    app.run_polling()

def check_config():
    logger.info("🛠️ Verificando configurações...")
    logger.info(f"TELEGRAM_BOT_TOKEN: {'✅ Configurado' if TELEGRAM_BOT_TOKEN else '❌ Não configurado'}")
    logger.info(f"API_SECRET_KEY: {'✅ Configurado' if API_SECRET_KEY else '❌ Não configurado'}")
    logger.info(f"API_URL: {'✅ ' + API_URL if API_URL else '❌ Não configurado'}")

if __name__ == "__main__":
    check_config()
    run_bot()