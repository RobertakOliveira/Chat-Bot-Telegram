# Arquivo: telegram_bot/__init__.py

# Importar e expor a função process_query
try:
    from .telegram_bot import process_query
except ImportError:
    # Função temporária caso o arquivo telegram_bot.py não exista
    def process_query(question):
        return "Sistema em manutenção. A funcionalidade completa será implementada em breve."

# Função temporária para substituir send_logs
def send_logs(message):
    print(f"LOG: {message}")

# Função temporária para substituir chroma_db
def chroma_db():
    print("Criando banco de dados vetorial (função temporária)...")
    return True