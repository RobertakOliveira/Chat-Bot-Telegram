import os
import boto3
import json
from io import BytesIO
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tempfile

# Nome do bucket S3 que será utilizado (deve ser único globalmente na AWS)
bucket_name = "meu-bucket-pdfs-eich-1407-pb-jan"

# Nome do perfil configurado com aws configure sso
session = boto3.Session(profile_name="eich-fernandes")

# Inicializa o cliente do serviço S3 usando as credenciais configuradas no ambiente
s3 = session.client("s3")


# Inicializa o client Bedrock Runtime
bedrock_runtime = session.client("bedrock-runtime")

# Configura o embedding usando o modelo Titan
bedrock_embeddings = BedrockEmbeddings(
  client=bedrock_runtime,
  model_id="amazon.titan-embed-text-v2:0"
)

def listar_pdfs_bucket(bucket_name):
  # Lista os arquivos PDF no bucket S3
  response = s3.list_objects_v2(Bucket=bucket_name)
  arquivos = response.get("Contents", [])
  return [arq["Key"] for arq in arquivos if arq["Key"].endswith(".pdf")]


def carregar_pdf_s3_em_memoria(bucket, key):
  # Lê o PDF do S3 em memória e carrega com PyPDFLoader
  print(f"🔄 Lendo PDF do S3 em memória: {key}")
  response = s3.get_object(Bucket=bucket, Key=key)
  conteudo_pdf = response["Body"].read()
  stream = BytesIO(conteudo_pdf)

  with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
    temp_file.write(conteudo_pdf)
    temp_path = temp_file.name

  try:
    loader = PyPDFLoader(temp_path)
    documentos = loader.load()
  finally:
    os.remove(temp_path)  # Remove o arquivo temporário depois de usar

  return documentos

def dividir_em_chunks(documentos, chunk_size=1000, chunk_overlap=100):
  # Divide os documentos em pedaços menores
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=chunk_size,
      chunk_overlap=chunk_overlap,
  )
  return text_splitter.split_documents(documentos)

def gerar_embeddings(chunks):
    # Gera embeddings usando o BedrockEmbeddings
    print(f"🔄 Gerando embeddings para {len(chunks)} chunks...")
    embeddings = []
    for i, chunk in enumerate(chunks):
        texto = chunk.page_content
        embedding = bedrock_embeddings.embed_query(texto)
        embeddings.append(embedding)
        print(f"  ✅ Chunk {i + 1}/{len(chunks)} processado.")
    return embeddings

# Salva o embedding em json direto na s3
def salvar_embeddings(embeddings, chunks, bucket, key):
  dados = []
  for i in range(len(embeddings)):
    dados.append({
      "embedding": embeddings[i],
      "texto": chunks[i].page_content,
      "metadata": chunks[i].metadata
    })

  # Gerando o nome do arquivo de destino no S3
  s3_key = f"embeddings/{key.replace('.pdf', '.json')}"

  json_bytes = json.dumps(dados, ensure_ascii=False).encode("utf-8")
  # Salvando os embeddings no S3
  s3.put_object(Bucket=bucket, Key=s3_key, Body=json_bytes)
  print(f"✅ Embeddings salvos em {s3_key}.")

def main():
  print("ℹ️ Listando PDFs na bucket...")
  pdfs_s3 = listar_pdfs_bucket(bucket_name)

  for key in pdfs_s3:
    print("------------------------------------------------------")
    documentos = carregar_pdf_s3_em_memoria(bucket_name, key)
    print(f"✅ {key} carregado com {len(documentos)} páginas.")

    # Cria os chunks
    chunks = dividir_em_chunks(documentos)
    # Cria o embedding
    embeddings = gerar_embeddings(chunks)

    salvar_embeddings(embeddings, chunks, bucket_name, key)

    print(f"✅ {len(embeddings)} embeddings gerados e salvos para '{key}'.")

if __name__ == "__main__":
  main()