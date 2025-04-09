import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Configuração do logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Banco de dados simples (em memória)
MENSAGENS = []

# Handler do /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Olá! Escolha uma opção:\n"
        "/sendmessage - Enviar uma mensagem\n"
        "/showmessage - Ver mensagens salvas\n"
        "/newchat - Apagar todas as mensagens"
    )

# Handler do /newchat (apenas limpa a lista)
async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MENSAGENS
    MENSAGENS.clear()
    await update.message.reply_text("🧹 Todas as mensagens foram apagadas! Novo chat iniciado.")
    context.user_data["aguardando_mensagem"] = False
    await start(update, context)

# Handler do /sendmessage
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Digite sua mensagem:\n"
        "❌ /cancel - Cancelar envio"
    )
    context.user_data["aguardando_mensagem"] = True

# Handler para /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("aguardando_mensagem"):
        context.user_data["aguardando_mensagem"] = False
        await update.message.reply_text("🚫 Envio cancelado.")
        await start(update, context)
    else:
        await update.message.reply_text("ℹ️ Nenhuma operação para cancelar.")

# Handler para mensagens de texto (após /sendmessage)
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("aguardando_mensagem"):
        user_message = update.message.text
        MENSAGENS.append({"user_id": update.message.from_user.id, "text": user_message})
        await update.message.reply_text("✅ Mensagem armazenada com sucesso!")
        context.user_data["aguardando_mensagem"] = False
        await start(update, context)

# Handler para ERRO: mídia (imagem/áudio) enviada no lugar de texto
async def handle_media_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("aguardando_mensagem"):
        await update.message.reply_text(
            "⚠️ Este bot só aceita mensagens de texto.\n\n"
            "📝 Digite sua mensagem:\n"
            "❌ /cancel - Cancelar envio"
        )
        # Mantém o estado "aguardando_mensagem" para tentar novamente

# Handler do /showmessage
async def show_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not MENSAGENS:
        await update.message.reply_text("📭 Nenhuma mensagem armazenada ainda.")
    else:
        mensagens_formatadas = [f"{idx + 1}. {msg['text']}" for idx, msg in enumerate(MENSAGENS)]
        await update.message.reply_text("📬 Mensagens armazenadas:\n\n" + "\n".join(mensagens_formatadas))
    await start(update, context)

# Configuração principal do bot
def main():
    # Voce deve colocar o token do seu bot aqui
    application = Application.builder().token("").build()

    # Handlers de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sendmessage", send_message))
    application.add_handler(CommandHandler("showmessage", show_messages))
    application.add_handler(CommandHandler("newchat", new_chat))
    application.add_handler(CommandHandler("cancel", cancel))


    # Handler para mensagens de TEXTO (após /sendmessage)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    )

    # Handler para ERRO: mídia (imagem/áudio) enviada no lugar de texto
    application.add_handler(
        MessageHandler(filters.VIDEO | filters.PHOTO | filters.AUDIO | filters.VOICE, handle_media_error)
    )

    # Inicia o bot
    application.run_polling()

if __name__ == "__main__":
    main()

# Update é um objeto que contém informações sobre a mensagem recebida, como o texto, o usuário que enviou, etc.
# ContextTypes é um tipo de contexto que contém informações adicionais, como dados do usuário, estado do bot, etc.