import os
from langchain.chains import RetrievalQA
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_aws.llms import BedrockLLM
import boto3

# Cliente Bedrock
boto3.setup_default_session(profile_name='leonardo-nogueira')
boto3_bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Embeddings com Titan
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1",
    client=boto3_bedrock
)

# LLM com Titan Text Express
llm = BedrockLLM(
    model_id="amazon.titan-text-express-v1",
    client=boto3_bedrock
)

msg = [
    SystemMessage(content="Você é um assistente de IA que ajuda a responder perguntas sobre perguntas gerais."),
    HumanMessage(content="O que você sabe sobre redes neurais?")
]

# Teste simples
resposta = llm.invoke(msg)
print(resposta)
