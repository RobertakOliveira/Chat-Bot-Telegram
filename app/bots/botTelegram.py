from dotenv import load_dotenv
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from chatbackend import get_chat_response, create_memory
load_dotenv()

# Configuração de logging
logging.basicConfig(
    filename='/var/log/chatbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.memory = create_memory()
        logger.info("Bot inicializado com sucesso")

    async def start(self, update, context):
        welcome_msg = """
        ⚖️ *Assistente Jurídico*
        
        Posso ajudar com:
        - Consultas a leis trabalhistas
        - Prazos processuais
        - Análise de documentos

        Digite /sair para encerrar.
        """
        logger.info(f"Usuário {update.effective_user.id} iniciou o bot")
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def handle_message(self, update, context):
        user_message = update.message.text
        user_id = update.effective_user.id
        
        if user_message.lower() in ('/sair', 'sair', 'tchau', 'adeus'):
            logger.info(f"Usuário {user_id} encerrou a conversa")
            await update.message.reply_text("Até logo! Digite /start quando precisar novamente.")
            return
            
        try:
            logger.info(f"Usuário {user_id} enviou mensagem: {user_message}")
            resposta = get_chat_response(user_message, self.memory)
            logger.info(f"Resposta gerada para usuário {user_id}")
            await update.message.reply_text(resposta)
        except Exception as e:
            logger.error(f"Erro ao processar mensagem do usuário {user_id}: {str(e)}")
            await update.message.reply_text("⚠️ Ocorreu um erro. Tente novamente.")

    async def sair(self, update, context):
        logger.info(f"Usuário {update.effective_user.id} encerrou o bot")
        await update.message.reply_text("Conversa encerrada. Volte sempre!")

def main():
    bot = TelegramBot()
    app = Application.builder().token(bot.token).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("sair", bot.sair))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    logger.info("Bot jurídico iniciando execução...")
    app.run_polling()

if __name__ == "__main__":
    main()