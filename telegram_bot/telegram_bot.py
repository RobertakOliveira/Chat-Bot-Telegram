import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatAction, ParseMode
import logging
import boto3
from typing import Optional, List

# Configuração de caminhos e imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.Rag_Pipeline import JusBotRAG  # Modificado para usar a classe JusBotRAG


# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('jusbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregando variáveis de ambiente
load_dotenv()

# Constantes
class Config:
    NOME_ASSISTENTE = "JusBot"
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    TEMPO_ESPERA_RESPOSTA = 45
    TAMANHO_MAX_RESPOSTA = 4000  # Limite do Telegram

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
    "processando": "🔍 Analisando o documento e buscando a resposta...\n ◀️Lembre-se que pode voltar ao menu principal quando desejar com o comando /voltar",
    "erro": "❌ Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.",
    "sem_documentos": "Não encontrei documentos relevantes para sua consulta.",
    "timeout": "⏳ Estou tendo dificuldades para processar sua solicitação. Por favor, reformule sua pergunta ou tente novamente mais tarde."
}

# Inicialização do RAG
rag_system = JusBotRAG()

def listar_arquivos_bucket() -> List[str]:
    """Lista todos os arquivos PDF no bucket S3 configurado"""
    try:
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=Config.BUCKET_NAME)
        
        if 'Contents' not in response:
            logger.warning("Nenhum arquivo encontrado no bucket S3")
            return []
        
        # Filtra apenas arquivos PDF (ou ajuste para seus tipos de documentos)
        arquivos = [
            obj['Key'] for obj in response['Contents'] 
            if obj['Key'].lower().endswith('.pdf')
        ]
        
        logger.info(f"Encontrados {len(arquivos)} arquivos no bucket S3")
        return arquivos
    
    except Exception as e:
        logger.error(f"Erro ao listar arquivos do S3: {str(e)}")
        return []
    
# Funções auxiliares
def criar_teclado(opcoes: list, colunas: int = 1) -> ReplyKeyboardMarkup:
    """Cria teclado personalizado a partir de uma lista de opções"""
    botoes = [opcoes[i:i + colunas] for i in range(0, len(opcoes), colunas)]
    return ReplyKeyboardMarkup(botoes, resize_keyboard=True)

async def enviar_mensagem_longa(update: Update, texto: str, max_length: int = Config.TAMANHO_MAX_RESPOSTA):
    """Envia mensagens longas dividindo em partes"""
    for i in range(0, len(texto), max_length):
        await update.message.reply_text(
            texto[i:i + max_length],
            parse_mode=ParseMode.MARKDOWN
        )

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler do comando /start"""
    context.user_data.clear()
    context.user_data["iniciado"] = True  # Marca que o /start foi usado
    nome_usuario = update.message.from_user.first_name or "Consulente"
    arquivos = rag_system.listar_documentos()
    logger.info(f"Encontrados {len(arquivos)} documentos disponíveis pelo RAG")
    
    await update.message.reply_text(
        MENSAGENS["boas_vindas"].format(nome_usuario=nome_usuario),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=criar_teclado(["Documento específico", "Documentos gerais"])
    )

async def voltar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler do comando /voltar"""
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler principal de mensagens"""
    if not context.user_data.get("iniciado"):
        await update.message.reply_text("👋 Por favor, inicie a conversa com o comando /start.")
        return

    texto = update.message.text.strip()
    chat_id = update.effective_chat.id

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        logger.info(f"Mensagem recebida: {texto}")

        # Respostas rápidas
        if texto.lower() in ["voltar", "voltar ao início"]:
            return await start(update, context)

        # Modo seleção de documento
        if texto in ["Documento específico", "Documentos gerais"]:
            context.user_data["modo"] = texto.lower().replace(" ", "_")

            if texto == "Documento específico":
                arquivos = rag_system.listar_documentos()
                if not arquivos:
                    return await update.message.reply_text("Nenhum documento disponível no momento.")

                teclado = criar_teclado(arquivos + ["Voltar"], 2)
                await update.message.reply_text("📂 Escolha o documento:", reply_markup=teclado)
            else:
                await update.message.reply_text(
                    "💡 Envie sua pergunta sobre documentos jurídicos em geral:",
                    reply_markup=criar_teclado(["Voltar"])
                )
            return

        # Seleção de documento específico
        if context.user_data.get("modo") == "documento_específico" and not context.user_data.get("documento"):
            context.user_data["documento"] = texto
            await update.message.reply_text(
                f"📄 *{texto}* selecionado! Agora envie sua pergunta sobre este documento.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=criar_teclado(["Voltar"])
            )
            return

        # Processamento da pergunta
        await update.message.reply_text(MENSAGENS["processando"])

        documento = context.user_data.get("documento") if context.user_data.get("modo") == "documento_específico" else None
        resposta = await processar_pergunta(texto, documento)

        if len(resposta) > Config.TAMANHO_MAX_RESPOSTA:
            await enviar_mensagem_longa(update, resposta)
        else:
            await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Erro no handle_message: {str(e)}")
        await update.message.reply_text(MENSAGENS["erro"])


async def processar_pergunta(pergunta: str, documento: Optional[str] = None) -> str:
    """Processa a pergunta usando o sistema RAG"""
    try:
        resposta = rag_system.query_document(pergunta, documento)
        
        if not resposta or "não encontrei" in resposta.lower():
            return MENSAGENS["sem_documentos"]
        
        return resposta
    
    except TimeoutError:
        logger.warning("Timeout ao processar pergunta")
        return MENSAGENS["timeout"]
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {str(e)}")
        return MENSAGENS["erro"]

# Função principal
def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("Token do Telegram não configurado!")
        return

    application = ApplicationBuilder() \
        .token(token) \
        .read_timeout(Config.TEMPO_ESPERA_RESPOSTA) \
        .write_timeout(Config.TEMPO_ESPERA_RESPOSTA) \
        .build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("voltar", voltar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info(f"{Config.NOME_ASSISTENTE} iniciado com sucesso!")
    application.run_polling()

if __name__ == '__main__':
    main()
    
    