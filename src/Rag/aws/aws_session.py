import boto3
from Rag.config.config import Config
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_aws.chat_models import ChatBedrock


boto3.setup_default_session(profile_name=Config.AWS_PROFILE)
boto3_bedrock = boto3.client("bedrock-runtime", region_name=Config.AWS_REGION)

def initialize_models():
    embeddings = BedrockEmbeddings(
        model_id=Config.EMBEDDING_MODEL,
        client=boto3_bedrock
    )
    llm = ChatBedrock(
        model_id=Config.LLM_MODEL,
        client=boto3_bedrock,
        model_kwargs={
            "max_tokens": 1000,
            "temperature": 0,
            "top_p": 0.9
        }
    )
    return embeddings, llm
