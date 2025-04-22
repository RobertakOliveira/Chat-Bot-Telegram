# telegram_bot.py
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatAction, ParseMode

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregando configurações de ambiente
load_dotenv()

# Nome do assistente
NOME_ASSISTENTE = "JusBot"

# Mensagens de boas-vindas
MENSAGEM_BOAS_VINDAS = """
🤖 *JusBot - Assistente Jurídico*

Olá, *{nome_usuario}*! Seja bem-vindo(a)!

Sou o assistente virtual, preparado para te ajudar com dúvidas sobre documentos e assuntos jurídicos.

Estou em desenvolvimento. Por enquanto, só posso responder mensagens simples.
"""

# Mensagem automática de saudação
SAUDACOES = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "alô", "alguém", "ajuda", "ei", "hey"]

# Função para registrar logs
def send_logs(mensagem):
    logger.info(mensagem)

# Função que lida com o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
   
    # Obtendo o nome do usuário
    nome_usuario = update.message.from_user.first_name or "Consulente"
   
    # Enviando mensagem personalizada
    await update.message.reply_text(
        MENSAGEM_BOAS_VINDAS.format(
            nome_usuario=nome_usuario
        ),
        parse_mode=ParseMode.MARKDOWN
    )

# Função que lida com as mensagens de texto do usuário
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
   
    # Obtendo texto da consulta e nome do usuário
    consulta = update.message.text
    nome_usuario = update.message.from_user.first_name or "Consulente"
   
    send_logs(f"Nova consulta de {nome_usuario}: {consulta}")
   
    # Verificando se é uma saudação
    if consulta.lower() in SAUDACOES:
        # Enviando mensagem de boas-vindas personalizada
        await update.message.reply_text(
            MENSAGEM_BOAS_VINDAS.format(
                nome_usuario=nome_usuario
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        return
   
    # Resposta padrão
    resposta_padrao = f"Olá *{nome_usuario}*! 🤖 \n\nAgradeço sua mensagem. Estou em desenvolvimento e em breve terei mais funcionalidades."
   
    # Enviando resposta ao usuário
    await update.message.reply_text(
        resposta_padrao,
        parse_mode=ParseMode.MARKDOWN
    )

def main():
    # Verifica se o token foi configurado
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("Token do Telegram não encontrado. Configure a variável TELEGRAM_TOKEN.")
        return
    
    # Autenticação com Token do Bot
    application = ApplicationBuilder().token(token).read_timeout(60).write_timeout(60).build()
   
    # Processa o comando /start
    application.add_handler(CommandHandler("start", start))
   
    # Processa as mensagens de texto recebidas
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
   
    # Ativa o bot até que o comando para parar seja enviado (Ctrl + C)
    send_logs(f"{NOME_ASSISTENTE} iniciado e pronto para consultas.")
    application.run_polling()

# Ponto de entrada
if __name__ == '__main__':
    main()