from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.constants import ParseMode
from config.config_bot import Config

MENSAGENS = {
    "boas_vindas": """
🤖 *JusBot - Assistente Jurídico*

Olá, *{nome_usuario}*! Seja bem-vindo(a)!

Sou seu assistente virtual especializado em documentos jurídicos.

🔍 *Como usar:*
1. Selecione um documento específico ou pergunte sobre os documentos em geral
2. Faça perguntas sobre os documentos, as perguntas podem ser sobre números de processos, partes envolvidas, decisões, etc.
3. Tente ser o mais específico possível para obter respostas mais precisas.
4. Receba respostas diretas e objetivas, com base nos documentos disponíveis.

📌 Digite /voltar a qualquer momento para retornar ao início.
""",
    "escolha_documento": "Você gostaria de consultar *um documento específico* ou *documentos em geral*?",
    "processando": "🔍 Analisando o documento e buscando a resposta...\n◀️ Lembre-se que pode voltar ao menu principal quando desejar com o comando /voltar",
    "erro": "❌ Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.",
    "sem_documentos": "Não encontrei documentos relevantes para sua consulta.",
    "timeout": "⏳ Estou tendo dificuldades para processar sua solicitação. Por favor, reformule sua pergunta ou tente novamente mais tarde."
}

def criar_teclado(opcoes: list, colunas: int = 1) -> ReplyKeyboardMarkup:
    """Cria um teclado personalizado com as opções fornecidas."""
    botoes = [opcoes[i:i + colunas] for i in range(0, len(opcoes), colunas)]
    return ReplyKeyboardMarkup(botoes, resize_keyboard=True)

async def enviar_mensagem_longa(update: Update, texto: str, max_length: int = Config.TAMANHO_MAX_RESPOSTA):
    """Envia uma mensagem longa dividida em partes."""
    for i in range(0, len(texto), max_length):
        await update.message.reply_text(
            texto[i:i + max_length],
            parse_mode=ParseMode.MARKDOWN
        )
