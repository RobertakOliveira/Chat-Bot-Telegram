from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode
from config.config_bot import Config
from rag_interface import listar_documentos_rag, consultar_rag
from messages import MENSAGENS, criar_teclado, enviar_mensagem_longa
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data["iniciado"] = True
    nome_usuario = update.message.from_user.first_name or "Consulente"
    await update.message.reply_text(
        MENSAGENS["boas_vindas"].format(nome_usuario=nome_usuario),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=criar_teclado(["Documento específico", "Documentos gerais"])
    )

async def voltar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("iniciado"):
        await update.message.reply_text("👋 Por favor, inicie com /start.")
        return

    texto = update.message.text.strip()
    chat_id = update.effective_chat.id

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        if texto.lower() in ["voltar", "voltar ao início"]:
            return await start(update, context)

        if texto in ["Documento específico", "Documentos gerais"]:
            context.user_data["modo"] = texto.lower().replace(" ", "_")
            if texto == "Documento específico":
                arquivos = listar_documentos_rag()
                if not arquivos:
                    return await update.message.reply_text("Nenhum documento disponível.")
                teclado = criar_teclado(arquivos + ["Voltar"], 2)
                await update.message.reply_text("📂 Escolha o documento:", reply_markup=teclado)
            else:
                await update.message.reply_text("💡 Envie sua pergunta:", reply_markup=criar_teclado(["Voltar"]))
            return

        if context.user_data.get("modo") == "documento_específico" and not context.user_data.get("documento"):
            context.user_data["documento"] = texto
            await update.message.reply_text(
                f"📄 *{texto}* selecionado!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=criar_teclado(["Voltar"])
            )
            return

        await update.message.reply_text(MENSAGENS["processando"])
        documento = context.user_data.get("documento") if context.user_data.get("modo") == "documento_específico" else None
        resposta = consultar_rag(texto, documento)

        if not resposta or "não encontrei" in resposta.lower():
            resposta = MENSAGENS["sem_documentos"]

        if len(resposta) > Config.TAMANHO_MAX_RESPOSTA:
            await enviar_mensagem_longa(update, resposta)
        else:
            await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        await update.message.reply_text(MENSAGENS["erro"])
