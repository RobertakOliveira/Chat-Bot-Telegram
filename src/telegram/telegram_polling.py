import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Estou vivo com polling.")

#fazer um request para o flask
def fazer_request_flask(mensagem):
    url = "http://localhost:5000/query"  # URL do seu endpoint Flask
    payload = {"query": mensagem}  # Payload com a mensagem
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Retorna a resposta JSON do Flask
    else:
        return {"error": "Erro ao processar a solicitação."}



# Qualquer mensagem de texto
async def responder_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #fazer um request para o flask
    resposta = fazer_request_flask(update.message.text)
    resposta_tratada = resposta.get("response", "Nenhuma resposta encontrada.")
    await update.message.reply_text(resposta_tratada)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_texto))

    print("Iniciando polling...")
    app.run_polling()
