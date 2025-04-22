import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatAction, ParseMode
import json

# Função para substituir o send_logs
def send_logs(message):
    if isinstance(message, dict):
        print(f"LOG: {json.dumps(message, ensure_ascii=False, indent=2)}")
    else:
        print(f"LOG: {message}")

# Carregando configurações de ambiente
load_dotenv()

# Função para processar a consulta jurídica (ajuste conforme necessário)
def process_query(question):
    # Exemplo simples de resposta
    # Substitua com a lógica do seu pipeline de processamento
    return f"Resposta para a consulta: {question}"

# Função que lida com o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    # Obtendo o nome do usuário
    nome_usuario = update.message.from_user.first_name or "Consulente"
    
    # Enviando mensagem personalizada
    await update.message.reply_text(
        f"🤖 Olá, {nome_usuario}! Sou o JusBot, assistente jurídico.",
        parse_mode=ParseMode.MARKDOWN
    )

# Função que lida com as mensagens de texto do usuário
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    # Obtendo texto da consulta
    consulta = update.message.text
    nome_usuario = update.message.from_user.first_name or "Consulente"
    
    send_logs(f"Nova consulta de {nome_usuario}: {consulta}")
    
    # Processando consulta jurídica
    resposta = process_query(consulta)
    
    # Personalizando resposta com o nome do usuário
    resposta_personalizada = f"*{nome_usuario}*, {resposta}"
    
    # Enviando resposta ao usuário
    await update.message.reply_text(
        resposta_personalizada,
        parse_mode=ParseMode.MARKDOWN
    )

def main():
    # Autenticação com Token do Bot
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).read_timeout(60).write_timeout(60).build()
    
    # Processa o comando /start
    application.add_handler(CommandHandler("start", start))
    
    # Processa as mensagens de texto recebidas
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Ativa o bot até que o comando para parar seja enviado (Ctrl + C)
    send_logs("JusBot iniciado e pronto para consultas.")
    application.run_polling()

# Ponto de entrada
if __name__ == '__main__':
    main()
