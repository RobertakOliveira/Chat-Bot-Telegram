from dotenv import load_dotenv
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from chatbackend import get_chat_response, create_memory
load_dotenv()

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.memory = create_memory()

    async def start(self, update, context):
        welcome_msg = """
        ⚖️ *Assistente Jurídico*
        
        Posso ajudar com:
        - Consultas a leis trabalhistas
        - Prazos processuais
        - Análise de documentos

        Digite /sair para encerrar.
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def handle_message(self, update, context):
        user_message = update.message.text
        
        if user_message.lower() in ('/sair', 'sair', 'tchau', 'adeus'):
            await update.message.reply_text("Até logo! Digite /start quando precisar novamente.")
            return
            
        try:
            resposta = get_chat_response(user_message, self.memory)
            await update.message.reply_text(resposta)
        except Exception as e:
            await update.message.reply_text("⚠️ Ocorreu um erro. Tente novamente.")
            print(f"Erro: {e}")

    async def sair(self, update, context):
        await update.message.reply_text("Conversa encerrada. Volte sempre!")

def main():
    bot = TelegramBot()
    app = Application.builder().token(bot.token).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("sair", bot.sair))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    print("Bot jurídico em execução...")
    app.run_polling()

if __name__ == "__main__":
    main()