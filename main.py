import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatAction, ParseMode
from telegram_bot import process_query as processar_consulta_juridica
from telegram_bot import send_logs as RegistroConsulta
from telegram_bot import chroma_db

# Carregando configurações de ambiente
load_dotenv()

# Nome do assistente
NOME_ASSISTENTE = "JusBot"

# Mensagens de boas-vindas
MENSAGEM_BOAS_VINDAS = """
🤖 *JusBot - Assistente Jurídico*

Olá, *{nome_usuario}*! Seja bem-vindo(a)!

Sou o assistente virtual, preparado para te ajudar com dúvidas sobre documentos e assuntos jurídicos.

Você pode me perguntar, por exemplo, sobre:
- O que significa um termo ou artigo
- Quais documentos são necessários em um processo
- Prazos ou etapas de um procedimento

Minhas respostas são baseadas nos documentos disponíveis em nossa base.
Fique à vontade para digitar sua dúvida. Estou aqui para ajudar!
"""

# Mensagem automática de saudação
SAUDACOES = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "alô", "alguém", "ajuda", "ei", "hey"]

# Verifica se a pasta com os vetores existem
if os.path.exists("./chroma_index"):
    RegistroConsulta("Chroma index encontrado. Carregando vector store...")
else:
    RegistroConsulta("Parece que os documentos não foram carregados, aguarde um instante.")
    # Cria os vetores e armazena na pasta chroma_index
    chroma_db()
    RegistroConsulta("Documentos carregados com sucesso!")

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
    
    RegistroConsulta(f"Nova consulta de {nome_usuario}: {consulta}")
    
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
    
    # Processando consulta jurídica
    resposta = processar_consulta_juridica(consulta)
    
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
    RegistroConsulta(f"{NOME_ASSISTENTE} iniciado e pronto para consultas.")
    application.run_polling()

# Ponto de entrada
if __name__ == '__main__':
    main()