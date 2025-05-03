import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    NOME_ASSISTENTE = "JusBot"
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TEMPO_ESPERA_RESPOSTA = 45
    TAMANHO_MAX_RESPOSTA = 4000  # Limite do Telegram
    # Webhook configurations for API Gateway integration
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8080))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-api-gateway-url/webhook")
    