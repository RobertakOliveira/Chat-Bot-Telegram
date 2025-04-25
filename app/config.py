from pathlib import Path # Para manipulação de caminhos de forma multiplataforma
from dotenv import load_dotenv # Para carregar variáveis de um arquivo .env
import os # Para acessar variáveis de ambiente do sistema



# Define o caminho relativo para o .env (alternativa de caminho absoluto explícito: env_path = "C:/Users/{USERNAME}/OneDrive/Documentos/GitHub/sprints-7-8-pb-aws-janeiro/.env")
env_path = Path(__file__).resolve().parent.parent / ".env"

# Carrega as variáveis de ambiente do arquivo .env encontrado no caminho especificado
load_dotenv(dotenv_path=env_path)

# Definir as variáveis necessárias
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/ask") # URL da API com valor (http://127.0.0.1:8000/ask) padrão para rodar localmente
API_SECRET_KEY = os.getenv("API_SECRET_KEY") # Chave secreta para autenticação (obrigatória)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") # Token do bot Telegram (obrigatório)

# Validação das variáveis críticas
if not all([API_SECRET_KEY, TELEGRAM_BOT_TOKEN]):
     # Levanta um erro se alguma variável obrigatória estiver faltando
    raise ValueError("Faltam variáveis de configuração no .env!")
