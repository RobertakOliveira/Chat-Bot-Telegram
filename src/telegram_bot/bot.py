import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config.config_bot import Config
from handlers import start, voltar, handle_message

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    application = ApplicationBuilder() \
        .token(Config.TELEGRAM_TOKEN) \
        .read_timeout(Config.TEMPO_ESPERA_RESPOSTA) \
        .write_timeout(Config.TEMPO_ESPERA_RESPOSTA) \
        .build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("voltar", voltar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
