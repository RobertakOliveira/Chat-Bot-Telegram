from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp
from app.config import API_SECRET_KEY, TELEGRAM_BOT_TOKEN, API_URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Olá! Envie sua dúvida jurídica.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = str(update.effective_chat.id)

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
            async with session.post(API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    await update.message.reply_text(data["answer"])
                else:
                    await update.message.reply_text("Erro ao processar a pergunta.")
        except Exception as e:
            await update.message.reply_text(f"Erro de conexão: {str(e)}")

# --- Handler de mídia ou conteúdo inválido ---
async def handle_media_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ Este bot só aceita mensagens de texto.\n\n"
        "📝 Envie sua dúvida jurídica:"
    )

def run_bot():
    print("✅ Bot do Telegram rodando...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(~filters.TEXT, handle_media_error))

    app.run_polling()
