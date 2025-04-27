import os
import boto3
import shutil
import json
from send_Reply  import sendReply
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrockConverse
from classe_embedding import BedrockEmbeddings

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
    print(f"✅ Sincronizado s3://{bucket_name}/{prefix} → {local_dir}/")


def handler(event, context):
    body = json.loads(event['body'])

    print("*** Received event")

    chat_id = body['message']['chat']['id']
    user_name = body['message']['from'].get('username', 'Desconhecido')
    message_text = body['message']['text']
    message_id = body['message']['message_id']

    print(f"*** chat id: {chat_id}")
    print(f"*** user name: {user_name}")
    print(f"*** message text: {message_text}")
    print(json.dumps(body))

    #FIm telegram, começo rag

    # 1. Define bucket e pasta local
    bucket_name = "bucketembeddingssprint777"
    prefix = "chroma_db/"
    persist_directory = "/temp/chroma_db"

    # 2. (Re)inicializa pasta local para teste limpo
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
    os.makedirs(persist_directory, exist_ok=True)

    # 3. Sempre baixa do S3
    sync_s3_folder(bucket_name, prefix, persist_directory)

    # 4. Instancia o Chroma diretamente com os arquivos baixados
    embeddings = BedrockEmbeddings()
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )



    # 5. Instanciação do modelo conversacional Bedrock
    model = ChatBedrockConverse(
        model="amazon.nova-pro-v1:0",
        region_name="us-east-1"
    )

    # 6. Prompt customizado como template de conversa
    prompt = ChatPromptTemplate.from_messages([
        ("human", "Você é um assistente jurídico de alta competência técnica e rigor analítico. "
        "Sua tarefa é utilizar exclusivamente as informações contidas nos trechos dos documentos fornecidos para elaborar uma resposta à pergunta apresentada.\n\n"
        "Diretrizes obrigatórias:\n"
        "- Utilize linguagem formal, precisa e estritamente técnica, conforme o padrão jurídico.\n"
        "- Fundamente suas respostas com base nos documentos, citando os trechos relevantes de maneira integrada ao texto.\n"
        "- Se a informação necessária não estiver presente ou for insuficiente, declare expressamente a limitação, sem tentar supor ou inferir dados ausentes.\n"
        "- Estruture a resposta de forma clara, coesa e organizada, utilizando parágrafos bem desenvolvidos.\n\n"
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

    # 7. Criação da chain
    chain = prompt | model

    # 8. Consulta
    query = message_text
    print(f"\nConsulta: {query}\n")

    # 9. Recupera os trechos relevantes
    # Recupera os documentos relevantes com scores de similaridade
    results_with_scores = vectorstore.similarity_search_with_score(query, k=3)

    # Exibe os scores e os documentos
    print("\nChunks retornados com similaridade:")
    context_parts = []
    for i, (doc, score) in enumerate(results_with_scores, 1):
        raw_source = doc.metadata.get("source", "desconhecido")
        page = doc.metadata.get("page", "n/d")
        print(f"Chunk {i}: Similaridade: {round(score, 4)} | Arquivo: {raw_source}, Página: {page}")
        context_parts.append(doc.page_content)


    # Junta os conteúdos para o prompt
    context = "\n\n".join(context_parts)


    # 10. Executa a cadeia conversacional
    resposta = chain.invoke({"input": query, "context": context})

    # 11. Exibe a resposta
    print("\nResposta gerada:\n", resposta.content)
    
    #fim rag, volta telegram com resposta
    # aqui chama o rag 
    reply_message = resposta.content
    

    sendReply(chat_id, reply_message,message_id)

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully')
    }    
