import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import boto3
from botocore.exceptions import ClientError

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Obter token do Telegram do arquivo .env
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("Token do Telegram não encontrado no arquivo .env!")

# Obter configurações da AWS do arquivo .env ou usar valores padrão
BUCKET_NAME = os.getenv('BUCKET_NAME', "meu-bucket-pdfs-eich-1407-pb-jan")
DATASET_DIR = os.getenv('DATASET_DIR', "dataset/")
CHROMA_DIR = os.getenv('CHROMA_DIR', "chroma_db")  # Diretório para armazenar a base Chroma

# Lista de saudações para acionar o menu principal
GREETINGS = ["oi", "olá", "oie", "eai", "ola", "hello", "hi", "hey", "e aí", "e ai", "bom dia", "boa tarde", "boa noite"]

# Variável global para armazenar o índice de vetores
vectorstore = None

# Funções para manipulação de documentos

def carregar_pdfs(caminho):
    """Carrega todos os arquivos PDF no caminho e subpastas."""
    from langchain_community.document_loaders import PyPDFLoader
    pdfs = []
    print("------------------------------------------------------")
    print(f"🔄 Procurando arquivos PDF em '{caminho}' (incluindo subpastas).")
    for root, dirs, files in os.walk(caminho):
        for arquivo in files:
            if arquivo.endswith(".pdf"):
                full_path = os.path.join(root, arquivo)
                full_path = full_path.replace("\\","/")
                print(f"    🔄 Carregando: {full_path}")
                loader = PyPDFLoader(full_path)
                pdfs.append((full_path, loader))
    if not pdfs:
        print(" Nenhum arquivo PDF encontrado.")
    return pdfs

def inicializar_base_conhecimento():
    """Inicializa a base de conhecimento utilizando os documentos carregados."""
    global vectorstore
    
    print("------------------------------------------------------")
    print(f"🔄 Inicializando base de conhecimento...")
    
    # Carrega os PDFs
    arquivos_pdf = carregar_pdfs(DATASET_DIR)
    if not arquivos_pdf:
        return False, "Nenhum arquivo PDF encontrado na pasta dataset/"
    
    # Importações necessárias
    from langchain_aws.embeddings import BedrockEmbeddings
    from langchain_community.vectorstores import Chroma
    
    try:
        # Inicializar boto3 para Bedrock
        boto3_bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        
        # Embeddings com Titan
        embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v1",
            client=boto3_bedrock
        )
        
        # Extrai documentos de cada PDF
        documentos = []
        nomes_arquivos = []
        for caminho, loader in arquivos_pdf:
            try:
                docs = loader.load()
                # Adicionar metadados com o nome do arquivo
                nome_arquivo = caminho.split("/")[-1]
                for doc in docs:
                    doc.metadata["source"] = nome_arquivo
                
                documentos.extend(docs)
                nomes_arquivos.append(nome_arquivo)
                print(f"✅ Documento carregado: {nome_arquivo} ({len(docs)} páginas)")
            except Exception as e:
                print(f" Erro ao carregar documento: {e}")
        
        if not documentos:
            return False, "Desculpe, não há documentos jurídicos disponíveis no momento."
            
        # Criar o índice vetorial com Chroma
        print(f"🔄 Criando índice vetorial com {len(documentos)} documentos...")
        
        # Verificar se o diretório já existe
        if os.path.exists(CHROMA_DIR) and os.path.isdir(CHROMA_DIR):
            print(f"⚠️ Diretório Chroma existente. Usando ChromaDB persistente.")
            # Carregar base existente
            vectorstore = Chroma(
                persist_directory=CHROMA_DIR,
                embedding_function=embeddings
            )
            # Adicionar novos documentos se necessário
            vectorstore.add_documents(documentos)
        else:
            # Criar nova base
            vectorstore = Chroma.from_documents(
                documents=documentos,
                embedding=embeddings,
                persist_directory=CHROMA_DIR
            )
        
        # Persistir a base
        vectorstore.persist()
        print(f"✅ Índice vetorial criado com sucesso!")
        
        return True, f"Base de conhecimento criada com {len(nomes_arquivos)} documentos"
    except Exception as e:
        print(f" Erro ao criar índice vetorial: {e}")
        return False, f"Erro ao inicializar base de conhecimento: {str(e)}"

def responder_consulta(pergunta):
    """Responde a uma pergunta usando a base de conhecimento vetorial."""
    global vectorstore
    
    if vectorstore is None:
        return "⚠️ A base de conhecimento ainda não foi inicializada. Por favor, selecione '🔍 Consultar Documentos Jurídicos' para iniciar."
    
    try:
        # Importações necessárias
        from langchain_aws.llms import BedrockLLM
        from langchain_core.messages import SystemMessage, HumanMessage
        from langchain.prompts import ChatPromptTemplate
        
        # Buscar documentos relevantes
        documentos = vectorstore.similarity_search(pergunta, k=4)
        
        if not documentos:
            return "Não encontrei informações relevantes nos documentos disponíveis para responder sua pergunta."
        
        # Criar contexto com os documentos recuperados
        contexto_docs = []
        for i, doc in enumerate(documentos):
            fonte = doc.metadata.get("source", "Documento sem fonte")
            page = doc.metadata.get("page", "?")
            contexto_docs.append(f"[Documento {i+1}: {fonte} (página {page})]\n{doc.page_content}")
        
        contexto = "\n\n".join(contexto_docs)
        
        # Inicializar boto3
        boto3_bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        
        # LLM com Titan Text Premier
        llm = BedrockLLM(
            model_id="amazon.titan-text-premier-v1:0",
            client=boto3_bedrock
        )
        
        # Criar prompt completo
        prompt_completo = f"""Você é um assistente jurídico especializado.
        
CONTEXTO DOS DOCUMENTOS:
{contexto}

PERGUNTA DO USUÁRIO:
{pergunta}

INSTRUÇÕES IMPORTANTES:
1. Responda à pergunta do usuário APENAS com base nas informações contidas nos documentos fornecidos.
2. Se a informação não estiver explicitamente nos documentos, diga apenas: "Não encontrei informações sobre isso nos documentos disponíveis."
3. NÃO inclua informações que não estejam nos documentos fornecidos.
4. Cite a fonte do documento e a página ao fornecer informações.
5. Seja conciso e objetivo, fornecendo apenas informações jurídicas relevantes.
6. NÃO responda a perguntas não relacionadas a assuntos jurídicos presentes nos documentos."""
        
        # Preparar mensagens para a LLM
        messages = [
            SystemMessage(content="Você é um assistente jurídico especializado em documentos legais. "
                        "Responda APENAS com base nas informações dos documentos fornecidos. "
                        "Se a informação não estiver nos documentos, diga claramente que não encontrou informações sobre o assunto."),
            HumanMessage(content=prompt_completo)
        ]
        
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        formatted_messages = chat_prompt.format_messages()
        response = llm.invoke(formatted_messages)
        
        # Adicionar citação das fontes
        fontes_utilizadas = set()
        for doc in documentos:
            fonte = doc.metadata.get("source", "Documento sem fonte")
            page = doc.metadata.get("page", "?")
            fontes_utilizadas.add(f"{fonte} (pág. {page})")
        
        resposta_final = str(response)
        if not resposta_final.lower().startswith("não encontrei"):
            resposta_final += "\n\n📚 Fontes consultadas:\n- " + "\n- ".join(fontes_utilizadas)
        
        return resposta_final
    except Exception as e:
        logger.error(f"Erro ao responder pergunta: {e}")
        return f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}"

# Funções para criar menus

def criar_menu_principal():
    """Cria o menu principal com botões."""
    keyboard = [
        ["🔍 Consultar Documentos Jurídicos"],
        ["📋 Listar Documentos Disponíveis"],
        ["ℹ️ Sobre o JusBot"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def criar_menu_documentos():
    """Cria um menu inline para listar documentos."""
    arquivos_pdf = carregar_pdfs(DATASET_DIR)
    keyboard = []
    
    # Criar botões para cada documento (máximo de 2 por linha)
    linha_atual = []
    for caminho, _ in arquivos_pdf:
        nome_arquivo = caminho.split("/")[-1]
        if len(linha_atual) < 2:
            linha_atual.append(InlineKeyboardButton(nome_arquivo, callback_data=f"doc_{nome_arquivo}"))
        else:
            keyboard.append(linha_atual)
            linha_atual = [InlineKeyboardButton(nome_arquivo, callback_data=f"doc_{nome_arquivo}")]
    
    # Adicionar última linha se não estiver vazia
    if linha_atual:
        keyboard.append(linha_atual)
        
    return InlineKeyboardMarkup(keyboard)

# Comandos e handlers do Telegram

async def start(update: Update, context: CallbackContext) -> None:
    """Comando para iniciar o bot e mostrar o menu principal."""
    await enviar_boas_vindas(update, context)

async def enviar_boas_vindas(update: Update, context: CallbackContext) -> None:
    """Envia mensagem de boas-vindas com menu principal."""
    # Obter o nome do usuário
    user_name = update.effective_user.first_name
    
    # Enviar mensagem de boas-vindas com menu
    await update.message.reply_text(
        f"🤖 *JusBot - Assistente Jurídico*\n\n"
        f"Olá, {user_name}! Sou especializado em responder perguntas sobre documentos jurídicos.\n\n"
        "Selecione uma opção abaixo ou digite sua pergunta diretamente.",
        reply_markup=criar_menu_principal(),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Envia uma mensagem de ajuda detalhada."""
    # Obter o nome do usuário
    user_name = update.effective_user.first_name
    
    await update.message.reply_text(
        f"🤖 *JusBot - Assistente Jurídico*\n\n"
        f"{user_name}, este bot responde a perguntas com base nos documentos jurídicos disponíveis.\n\n"
        "*Como usar:*\n"
        "1. Selecione '🔍 Consultar Documentos Jurídicos' para inicializar a base de conhecimento\n"
        "2. Digite sua pergunta relacionada aos documentos\n"
        "3. Receba respostas baseadas apenas no conteúdo dos documentos\n\n"
        "*Importante:* Só respondo a perguntas cujas respostas estão nos documentos disponíveis.",
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: CallbackContext) -> None:
    """Processa os callbacks dos botões inline."""
    query = update.callback_query
    await query.answer()  # Responde ao callback para remover o "carregando"

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Processa mensagens de texto e responde conforme o conteúdo."""
    user_text = update.message.text.strip()
    
    # Obter o nome do usuário
    user_name = update.effective_user.first_name
    
    # Verifica se é uma saudação para mostrar o menu
    if user_text.lower() in GREETINGS:
        await enviar_boas_vindas(update, context)
        return
        
    # Verifica se é um comando de menu
    if user_text == "🔍 Consultar Documentos Jurídicos":
        # Inicializar a base de conhecimento
        processing_message = await update.message.reply_text("🔄 Inicializando base de conhecimento, por favor aguarde... Isso pode demorar alguns instantes.")
        
        success, message = inicializar_base_conhecimento()
        await processing_message.delete()
        
        if success:
            await update.message.reply_text(
                f"✅ {user_name}, a base de conhecimento foi inicializada! Agora você pode fazer perguntas sobre o conteúdo dos documentos."
            )
        else:
            await update.message.reply_text(f"❌ {user_name}, {message}")
        return
        
    elif user_text == "📋 Listar Documentos Disponíveis":
        # Mostrar mensagem de processamento
        processing_message = await update.message.reply_text("🔄 Buscando documentos disponíveis...")
        
        arquivos_pdf = carregar_pdfs(DATASET_DIR)
        
        # Remover mensagem de processamento
        await processing_message.delete()
        
        if not arquivos_pdf:
            await update.message.reply_text(f"{user_name}, nenhum documento foi encontrado na pasta dataset/.")
            return
            
        mensagem = f"📚 *{user_name}, aqui estão os documentos disponíveis:*\n\n"
        for i, (caminho, _) in enumerate(arquivos_pdf, 1):
            nome_arquivo = caminho.split("/")[-1]
            mensagem += f"{i}. {nome_arquivo}\n"
            
        await update.message.reply_text(
            mensagem,
            parse_mode="Markdown"
        )
        return
        
    elif user_text == "ℹ️ Sobre o JusBot":
        await update.message.reply_text(
            f"🤖 *JusBot - Assistente Jurídico*\n\n"
            f"{user_name}, sou um bot especializado em responder consultas sobre documentos jurídicos.\n\n"
            "*Características:*\n"
            "• Consulto apenas os documentos disponíveis na base de dados\n"
            "• Respondo perguntas somente quando encontro informações nos documentos\n"
            "• Cito as fontes das informações que forneço\n\n"
            "*Tecnologias:*\n"
            "• Amazon Bedrock para processamento de linguagem natural\n"
            "• ChromaDB para busca vetorial em documentos\n"
            "• LangChain para RAG (Retrieval Augmented Generation)",
            parse_mode="Markdown"
        )
        return
    
    # Se não for comando ou saudação, trata como pergunta jurídica
    processing_message = await update.message.reply_text(f"🔄 {user_name}, estou consultando os documentos... Isso pode levar alguns instantes enquanto analiso o conteúdo.")
    
    try:
        # Responder à pergunta usando a base de conhecimento
        resposta = responder_consulta(user_text)
        
        # Enviar resposta
        await update.message.reply_text(resposta)
    except Exception as e:
        logger.error(f"Erro ao responder pergunta: {e}")
        await update.message.reply_text(
            f" Desculpe, {user_name}, ocorreu um erro ao processar sua consulta. "
            "Por favor, tente novamente mais tarde."
        )
    finally:
        # Remover mensagem de processamento
        await processing_message.delete()

def main() -> None:
    """Função principal para iniciar o bot do Telegram."""
    print("=" * 50)
    print("🤖 Iniciando JusBot - Assistente Jurídico")
    print(f"📁 Pasta de documentos: {DATASET_DIR}")
    print(f"💾 Diretório ChromaDB: {CHROMA_DIR}")
    print(f"☁️ Bucket S3: {BUCKET_NAME}")
    print("=" * 50)
    
    # Criar a aplicação do Telegram
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Adicionar manipuladores
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Iniciar o bot
        print("✅ Bot iniciado! Pressione Ctrl+C para parar.")
        application.run_polling()
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")

if __name__ == "__main__":
    main()