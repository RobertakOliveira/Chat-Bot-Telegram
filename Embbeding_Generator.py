import os
import boto3
import json
from langchain_core.documents import Document
from langchain_aws import BedrockEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()
# Nome do bucket S3
bucket_name = os.getenv("BUCKET_NAME")

# Nome do perfil AWS
session = boto3.Session(profile_name=os.getenv("AWS_PROFILE"))

# Inicializar clientes
s3 = session.client("s3")
bedrock_runtime = session.client("bedrock-runtime")

# Inicializar Bedrock Embeddings
bedrock_embeddings = BedrockEmbeddings(
    client=bedrock_runtime,
    model_id="amazon.titan-embed-text-v2:0"
)

# 📂 Listar arquivos .txt no bucket
def listar_txts_bucket(bucket_name):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix="textos_extraidos/")
    arquivos = response.get("Contents", [])
    return [arq["Key"] for arq in arquivos if arq["Key"].endswith(".txt")]

# 📄 Carregar conteúdo do TXT
def carregar_txt_s3(bucket, key):
    print(f"🔄 Lendo TXT do S3: {key}")
    response = s3.get_object(Bucket=bucket, Key=key)
    conteudo_txt = response["Body"].read().decode("utf-8")
    documento = Document(
        page_content=conteudo_txt,
        metadata={"source": key.split("/")[-1]}  # só o nome do arquivo
    )
    return documento

# ✂️ Dividir documentos em chunks
def dividir_em_chunks(documentos, chunk_size=1200, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return text_splitter.split_documents(documentos)

# 🧠 Gerar embeddings
def gerar_embeddings(chunks):
    print(f"🔄 Gerando embeddings para {len(chunks)} chunks...")
    embeddings = []
    chunks_validos = []
    for i, chunk in enumerate(chunks):
        texto = chunk.page_content.strip()
        if len(texto) < 50:
            print(f"⚠️ Chunk {i+1} ignorado por ser muito pequeno.")
            continue

        embedding = bedrock_embeddings.embed_query(texto)
        embeddings.append(embedding)

        chunk.metadata["chunk_id"] = i
        chunks_validos.append(chunk)

        print(f"✅ Chunk {i+1}/{len(chunks)} processado.")

    return embeddings, chunks_validos

# 💾 Salvar embeddings em JSON no S3
def salvar_embeddings(embeddings, chunks, bucket, key):
    dados = []
    for i in range(len(embeddings)):
        dados.append({
            "embedding": embeddings[i],
            "texto": chunks[i].page_content,
            "metadata": chunks[i].metadata
        })

    # Salvar na pasta 'embeddings/'
    novo_key = key.replace("textos_extraidos/", "embeddings/").replace(".txt", ".json")
    json_bytes = json.dumps(dados, ensure_ascii=False).encode("utf-8")

    s3.put_object(Bucket=bucket, Key=novo_key, Body=json_bytes)
    print(f"✅ Embeddings salvos em {novo_key}.")

# 🚀 Pipeline principal
def main():
    print("ℹ️ Listando arquivos .txt extraídos no bucket...")
    txts_s3 = listar_txts_bucket(bucket_name)

    for key in txts_s3:
        print("------------------------------------------------------")
        documento = carregar_txt_s3(bucket_name, key)
        print(f"✅ {key} carregado.")

        chunks = dividir_em_chunks([documento])

        embeddings, chunks_validos = gerar_embeddings(chunks)

        salvar_embeddings(embeddings, chunks_validos, bucket_name, key)

        print(f"✅ {len(embeddings)} embeddings gerados e salvos para '{key}'.")

if __name__ == "__main__":
    main()