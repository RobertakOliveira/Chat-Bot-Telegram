import os
import boto3
import shutil
import json
import logging
from send_Reply import sendReply
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrockConverse
from classe_embedding import BedrockEmbeddings

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_s3_folder(bucket_name: str, prefix: str, local_dir: str):
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):
                continue
            rel_path = key[len(prefix):]
            local_path = os.path.join(local_dir, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(bucket_name, key, local_path)
    logger.info(f"✅ Sincronizado s3://{bucket_name}/{prefix} → {local_dir}/")


def handler(event, context):
    logger.info("*** Received event: %s", json.dumps(event))
    try:
        body = json.loads(event.get('body', '{}'))
        logger.info("*** Parsed body: %s", json.dumps(body))

        # Telegram details
        chat_id = body['message']['chat']['id']
        user_name = body['message']['from'].get('username', 'Desconhecido')
        message_text = body['message'].get('text', '')
        message_id = body['message'].get('message_id')

        logger.info("*** chat id: %s", chat_id)
        logger.info("*** user name: %s", user_name)
        logger.info("*** message text: %s", message_text)
        logger.info("*** message id: %s", message_id)

        # RAG setup
        bucket_name = "bucketembeddingssprint7"
        prefix = "chroma_db/"
        persist_directory = "/tmp/chroma_db"

        # Limpa diretório local
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
        os.makedirs(persist_directory, exist_ok=True)

        # Baixa índices Chroma
        sync_s3_folder(bucket_name, prefix, persist_directory)

        # Inicializa vectorstore
        embeddings = BedrockEmbeddings()
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

        # Modelo e prompt
        model = ChatBedrockConverse(model="amazon.nova-pro-v1:0", region_name="us-east-1")
        prompt = ChatPromptTemplate.from_messages([
        ("human", "Você é um assistente jurídico de alta competência técnica e rigor analítico. "
        "Sua tarefa é utilizar exclusivamente as informações contidas nos trechos dos documentos fornecidos para elaborar uma resposta à pergunta apresentada.\n\n"
        "Diretrizes obrigatórias:\n"
        "- Utilize linguagem formal, precisa e estritamente técnica, conforme o padrão jurídico.\n"
        "- Fundamente suas respostas com base nos documentos, citando os trechos relevantes de maneira integrada ao texto.\n"
        "- Se a informação necessária não estiver presente ou for insuficiente, declare expressamente a limitação, sem tentar supor ou inferir dados ausentes.\n"
        "- Estruture a resposta de forma clara, coesa e organizada, utilizando parágrafos bem desenvolvidos.\n"
        "- Se a informação necessária não estiver presente ou for insuficiente, declare expressamente a limitação, sem tentar supor ou inferir dados ausentes.\n\n"
        "Formato da tarefa:\n"
        "- Introdução breve contextualizando o tema da pergunta (se aplicável).\n"
        "- Análise fundamentada com base nos documentos fornecidos.\n"
        "- Conclusão objetiva, explicitando o alcance ou a limitação da resposta conforme a documentação disponível.\n\n"
        "Exemplos Modelares (não relacionados aos casos de teste):\n"
        "- Elaboração de parecer sobre a validade de uma cláusula contratual com base em trechos do Código Civil.\n"
        "- Análise de um pedido de indenização a partir de excertos da legislação trabalhista.\n"
        "- Resposta a uma consulta sobre regime de bens no casamento com base em jurisprudência selecionada.\n\n"
        "Dados fornecidos:\n"
        "Documentos:\n{context}\n\n"
        "Pergunta:\n{input}\n\n"
        "Inicie sua resposta abaixo:\n"
        "Resposta:"
        )
        ])
        chain = prompt | model

        # Recupera chunks
        logger.info("*** Iniciando similarity_search...")
        results_with_scores = vectorstore.similarity_search_with_score(message_text, k=3)
        context_parts = []
        for i, (doc, score) in enumerate(results_with_scores, 1):
            src = doc.metadata.get('source', 'desconhecido')
            pg = doc.metadata.get('page', 'n/d')
            logger.info("Chunk %d: score=%.4f | %s (pág. %s)", i, score, src, pg)
            logger.debug("Conteúdo: %s", doc.page_content)
            context_parts.append(doc.page_content)

        context_text = "\n\n".join(context_parts)

        # Gera resposta RAG
        resposta = chain.invoke({"input": message_text, "context": context_text})
        reply_message = resposta.content
        logger.info("***Resposta gerada: %s", reply_message)

        # Envia reply ao Telegram
        try:
            logger.info("*** Enviando reply ao Telegram...")
            resp = sendReply(chat_id, reply_message, message_id)
            logger.info("sendReply response: %s", resp)
        except Exception as e:
            logger.error("Erro ao enviar mensagem pelo Telegram", exc_info=True)

        return {
            'statusCode': 200,
            'body': json.dumps('Message processed successfully')
        }

    except Exception as e:
        logger.error("Erro geral no handler", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
