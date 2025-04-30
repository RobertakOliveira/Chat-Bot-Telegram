# Importações das bibliotecas necessárias
from telegram import Update  # Objetos de atualização do Telegram
from telegram.ext import (  # Extensões para construção do bot
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import aiohttp  # Cliente HTTP assíncrono para chamadas à API
import sys  # Para saída do programa em caso de erro
from app.config import (  # Configurações sensíveis (variáveis de ambiente)
    API_SECRET_KEY,
    TELEGRAM_BOT_TOKEN,
    API_URL
)
import logging  # Sistema de logs

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Handlers de comandos e mensagens ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    logger.info(f"Comando /start recebido do chat_id: {update.effective_chat.id}")
    await update.message.reply_text("👋 Olá! Envie sua dúvida jurídica.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para mensagens de texto"""
    user_message = update.message.text  # Texto da mensagem recebida
    chat_id = str(update.effective_chat.id)  # ID do chat (convertido para string)
    
    # Log da mensagem recebida
    logger.info(f"Mensagem recebida - Chat ID: {chat_id}, Mensagem: {user_message}")

    # Tratamento especial para /start (redundância opcional)
    if user_message == "/start":
        await update.message.reply_text("Olá! Envie sua dúvida jurídica.")
        return

    # Prepara payload para a API
    payload = {
        "text": user_message,  # Mensagem do usuário
        "chat_id": chat_id  # ID do chat para referência
    }

    # Headers com a chave de API para autenticação
    headers = {
        "X-API-KEY": API_SECRET_KEY
    }

    # Faz chamada assíncrona à API
    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Enviando para API - Chat ID: {chat_id}, Mensagem: {user_message}")
            async with session.post(API_URL, json=payload, headers=headers) as response:
                if response.status == 200:  # Sucesso
                    data = await response.json()  # Decodifica resposta JSON
                    logger.info(f"Resposta da API recebida - Chat ID: {chat_id}, Resposta: {data['answer']}")
                    await update.message.reply_text(data["answer"])  # Envia resposta ao usuário
                else:  # Erro HTTP
                    error_msg = f"Erro na API - Status: {response.status}"
                    logger.error(error_msg)
                    await update.message.reply_text(
                        "⚠️ Ops! Não consegui entender sua pergunta agora.\nTente novamente mais tarde."
                    )
        except Exception as e:  # Erro de conexão/exceção
            logger.error(f"Erro de conexão com a API - Chat ID: {chat_id}, Erro: {str(e)}")
            await update.message.reply_text(f"❌ Erro de conexão com a API.\nDetalhes: {str(e)}")

async def handle_media_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensagens não-texto (mídia, stickers, etc.)"""
    logger.warning(f"Mídia não suportada recebida - Chat ID: {update.effective_chat.id}")
    await update.message.reply_text(
        "⚠️ Este bot só aceita mensagens de texto.\n\n"
        "📝 Envie sua dúvida jurídica:"
    )

def run_bot():
    """Função principal para iniciar o bot"""
    # Verifica se todas as variáveis de ambiente estão configuradas
    if not TELEGRAM_BOT_TOKEN or not API_URL or not API_SECRET_KEY:
        logger.critical("Variáveis de ambiente não configuradas corretamente")
        sys.exit(1)  # Encerra o programa com erro

    logger.info("✅ Bot do Telegram iniciando...")
    # Constrói a aplicação do bot com o token
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registra os handlers (manipuladores de eventos)
    app.add_handler(CommandHandler("start", start))  # /start
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))  # Mensagens de texto
    app.add_handler(MessageHandler(~filters.TEXT, handle_media_error))  # Mensagens não-texto

    # Inicia o bot no modo polling (busca atualizações)
    app.run_polling()

def check_config():
    """Função auxiliar para verificar configurações"""
    logger.info("🛠️ Verificando configurações...")
    logger.info(f"TELEGRAM_BOT_TOKEN: {'✅ Configurado' if TELEGRAM_BOT_TOKEN else '❌ Não configurado'}")
    logger.info(f"API_SECRET_KEY: {'✅ Configurado' if API_SECRET_KEY else '❌ Não configurado'}")
    logger.info(f"API_URL: {'✅ ' + API_URL if API_URL else '❌ Não configurado'}")

if __name__ == "__main__":
    # Ponto de entrada principal
    check_config()  # Verifica configurações primeiro
    run_bot()  # Inicia o bot

# Instruções para rodar localmente: (diretorio raiz)
# python -m app.bot (diretório raíz)