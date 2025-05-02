import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NOME_ASSISTENTE = "JusBot"
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TEMPO_ESPERA_RESPOSTA = 45
    TAMANHO_MAX_RESPOSTA = 4000  # Limite do Telegram