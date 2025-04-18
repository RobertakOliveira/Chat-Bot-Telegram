import os
from dotenv import load_dotenv

# Carregar o arquivo .env
load_dotenv()

# Definir as variáveis necessárias
API_URL = os.getenv("API_URL")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Opcional: Verifique se as variáveis foram carregadas corretamente
if not API_URL or not API_SECRET_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Faltam variáveis de configuração no .env!")