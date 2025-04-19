import boto3
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configurações
bucket_name = "testesprint7e8"
prefix = "juridicos/"
persist_directory = "./chroma_db"
load_dotenv()

# Inicializar embeddings e splitter
embeddings = BedrockEmbeddings(
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    model_id="amazon.titan-embed-text-v2:0"
)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Listar e processar objetos PDF do S3
s3 = boto3.client('s3')
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
documents = []

for obj in response.get('Contents', []):
    file_key = obj['Key']
    file_name = file_key.split('/')[-1]
    
    temp_file = f"/tmp/{file_name}"
    s3.download_file(bucket_name, file_key, temp_file)
    
    try:
        loader = PyPDFLoader(temp_file)
        documents.extend(loader.load())
    except Exception as e:
        print(f"Erro ao processar {file_key}: {str(e)}")
    
    os.remove(temp_file)

# Dividir textos em chunks (opcional, mas recomendado para RAG)
split_documents = text_splitter.split_documents(documents)

# Indexar no Chroma
vector_db = Chroma.from_documents(
    documents=split_documents,
    embedding=embeddings,
    persist_directory=persist_directory
)

print(f"Indexação concluída! Total de documentos processados: {len(documents)}")