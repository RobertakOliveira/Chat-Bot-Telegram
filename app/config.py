import os
from dotenv import load_dotenv
from pathlib import Path

# Carregue o arquivo .env da raiz do projeto
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Definir as variáveis necessárias
API_URL = os.getenv("API_URL")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not all([API_URL, API_SECRET_KEY, TELEGRAM_BOT_TOKEN]):
    raise ValueError("Faltam variáveis de configuração no .env!")