import boto3
from langchain.chains import RetrievalQA
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_aws.llms import BedrockLLM
from langchain.prompts import ChatPromptTemplate

# Configurar o perfil AWS
boto3.setup_default_session(profile_name='leonardo-nogueira')

# Cliente Bedrock
boto3_bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def obter_embedding(pergunta: str):
    embedding = embeddings.embed_query(pergunta)
    return embedding

# Embeddings com Titan (continua com embed-text)
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    client=boto3_bedrock
)

# LLM com Titan Text Premier
llm = BedrockLLM(
    model_id="amazon.titan-text-premier-v1:0",
    client=boto3_bedrock
)

# Função de resposta com LangChain
def responder_com_langchain(pergunta: str) -> str:
    # Fazer embedding do input com Titan
    embedding_input = embeddings.embed_query(pergunta)
    print("Embedding da pergunta:", embedding_input)

    # Criar os messages
    messages = [
        SystemMessage(content="Você é um assistente de IA que ajuda a a responder perguntas relacionadas a documentos Jurídicos." \
        "Se não souber a resposta, diga que não sabe." \
        "Responda de forma clara e objetiva." \
        "Caso perguntem algo que não seja relacionado a documentos jurídicos, diga que não pode ajudar."),
        HumanMessage(content=pergunta)
    ]
    
    # Preparar prompt e invocar LLM
    chat_prompt = ChatPromptTemplate.from_messages(messages)
    formatted_messages = chat_prompt.format_messages()
    response = llm.invoke(formatted_messages)
    
    return str(response)

