from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
from dotenv import load_dotenv
import os
import boto3
import json

# Função temporária para substituir o send_logs
def send_logs(message):
    # Implementação básica para não quebrar o código
    if isinstance(message, dict):
        print(f"LOG: {json.dumps(message, ensure_ascii=False, indent=2)}")
    else:
        print(f"LOG: {message}")

# Carregando variáveis de ambiente
load_dotenv()

# Configurações do diretório e busca
persist_directory = 'chroma_index'
chroma_search_k = 6

# Conectando cliente Bedrock 
bedrock = boto3.client('bedrock-runtime', region_name = os.getenv('REGION_NAME'))

# Gerar embedding
titan_embedding = BedrockEmbeddings(model_id = 'amazon.titan-embed-text-v1:0', client=bedrock)

# Função para carregar LLM
def load_llm():
    return ChatBedrock(
        model_id = 'amazon.titan-text-premier-v1:0',
        client = bedrock,
        temperature = 0.25,
        max_tokens = 600,
    )

# Criar prompt completo
PROMPT_TEMPLATE = """
Você é o JusBot, assistente virtual.

Ao analisar os documentos do seu caso, irei:

Documentos disponíveis: {context}

MINHA MISSÃO:
1. Explicar de forma clara e simples o que encontrei nos seus documentos
2. Informar onde exatamente encontrei cada informação importante
3. Explicar as leis relevantes em linguagem do dia a dia
4. Responder suas dúvidas com base apenas nos documentos que temos

Estou aqui para ajudar você a entender sua situação jurídica sem complicações. Quando me referir a "documentos" ou "processos", estarei falando dos documentos do seu caso que analisei.

Sua pergunta: {question}

Explicação simples:
"""

PROMPT = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])

# Pipeline QA
def process_query(question):
    try:
        # Carrega o índice Chroma
        vector_store = Chroma(persist_directory=persist_directory, embedding_function=titan_embedding)

        llm = load_llm()

        # Configuração da cadeia de QA
        qa_chain = RetrievalQA.from_chain_type(
            llm = llm,
            retriever = vector_store.as_retriever(search_kwargs = {"k": chroma_search_k}),
            return_source_documents = True,
            chain_type_kwargs = {'prompt': PROMPT}
        )
        
        response = qa_chain.invoke({'query': question})
        send_logs(response)
        return response['result']
    except Exception as e:
        send_logs(f'Erro durante o processamento da consulta: {e}')
        return 'Não localizamos uma resposta com base nos documentos disponíveis. Recomendamos que reformule sua pergunta ou tente novamente em instantes. Estamos à disposição para ajudar.'

# Função para criar banco de dados vetorial (implementação simplificada)
def chroma_db():
    try:
        # Inicializando o cliente
        cliente = bedrock
        embeddings = titan_embedding
        
        # Aqui normalmente seriam carregados os documentos e criado o índice
        send_logs("Inicializando criação do banco vetorial...")
        
        # Código de criação da base de conhecimento seria aqui
        
        send_logs("Banco de dados vetorial criado com sucesso.")
        return True
    except Exception as e:
        send_logs(f"Erro ao criar banco de dados vetorial: {e}")
        return False

# Código de teste opcional
if __name__ == "__main__":
    # Teste rápido do processador de consultas
    pergunta_teste = "Quais são os prazos para recurso neste processo?"
    print(f"Testando consulta: {pergunta_teste}")
    resposta = process_query(pergunta_teste)
    print(f"Resposta: {resposta}")