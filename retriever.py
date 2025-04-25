import os
import boto3
import json
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings.bedrock import BedrockEmbeddings

# Inicializa sessão e clientes AWS
session = boto3.Session(profile_name="")
s3 = session.client("s3")
bedrock_runtime = session.client("bedrock-runtime")

# Nome do bucket onde estão os embeddings
bucket_name = ""

# Diretório local onde vamos salvar temporariamente os JSONs
os.makedirs("embeddings_local", exist_ok=True)

# Inicializa o embedding
embedding_model = BedrockEmbeddings(
    client=bedrock_runtime,
    model_id="amazon.titan-embed-text-v2:0"
)

def listar_arquivos_json(bucket):
    response = s3.list_objects_v2(Bucket=bucket, Prefix="embeddings/")
    return [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].endswith(".json")]

def baixar_e_carregar_documentos(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    conteudo = response["Body"].read().decode("utf-8")
    dados = json.loads(conteudo)

    documentos = [
        Document(page_content=item["texto"], metadata=item.get("metadata", {}))
        for item in dados
    ]
    return documentos

def indexar_com_chroma(documentos, persist_dir="chroma_db"):
    db = Chroma.from_documents(
        documents=documentos,
        embedding=embedding_model,
        persist_directory=persist_dir
    )
    db.persist()
    return db

def criar_retriever():
    print("🔍 Listando arquivos de embedding no S3...")
    arquivos_json = listar_arquivos_json(bucket_name)

    todos_documentos = []
    for key in arquivos_json:
        print(f"⬇️  Baixando e carregando: {key}")
        docs = baixar_e_carregar_documentos(bucket_name, key)
        todos_documentos.extend(docs)

    print(f"🧠 Indexando {len(todos_documentos)} documentos com ChromaDB...")
    chroma_db = indexar_com_chroma(todos_documentos)

    # Corrigido: agora usamos chroma_db para criar o retriever
    retriever = chroma_db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    print("✅ Retriever pronto!")
    return retriever

# Agora você cria o retriever
retriever = criar_retriever()

