import os
import json
import boto3
import chromadb
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()

session = boto3.Session(profile_name=os.getenv("AWS_PROFILE"))

print("------------------------------------------------------")
print("🔄 Inicializando o cliente S3...")

bucket = os.getenv("BUCKET_NAME")
prefixo = "../embeddings_temp/"
chroma_path = "../chroma_db_producao"
collection_name = "producao"  # <--- Definido aqui para consistência

os.makedirs(prefixo, exist_ok=True)

def baixar_arquivos_s3():
    print("🔽 Baixando arquivos JSON do S3...")
    s3 = session.client("s3")
    arquivos = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket, Prefix="embeddings/"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".json"):
                caminho_local = os.path.join(prefixo, os.path.basename(key))
                s3.download_file(bucket, key, caminho_local)
                arquivos.append(caminho_local)
                print(f"✔️ Baixado: {key} → {caminho_local}")
    return arquivos

def carregar_dados(arquivos):
    documentos = []
    embeddings = []
    tamanho_esperado = None

    for arquivo in arquivos:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            for item in dados:
                emb = item["embedding"]
                if tamanho_esperado is None:
                    tamanho_esperado = len(emb)

                # Cuidado aqui: vamos usar 'text', não 'texto'
                documentos.append(
                    Document(
                        page_content=item.get("texto", ""),   
                        metadata={ "source": item["metadata"]["source"] }
                    ))

                embeddings.append(emb)

    print(f"📊 Total de documentos: {len(documentos)}")
    print(f"📏 Dimensão dos embeddings: {tamanho_esperado}")
    return documentos, embeddings

def indexar_no_chroma(docs, embs):
    print("🚀 Indexando embeddings reais no Chroma...")

    client = chromadb.PersistentClient(path=chroma_path)

    try:
        collection = client.get_or_create_collection(name=collection_name)
    except Exception as e:
        print(f"❌ Erro ao criar/obter a coleção: {e}")
        return

    collection.add(
        documents=[doc.page_content for doc in docs],
        embeddings=embs,
        metadatas=[doc.metadata for doc in docs],
        ids=[f"doc_{i}" for i in range(len(docs))]
    )

    print(f"✅ {len(docs)} documentos indexados na coleção '{collection_name}'.")

arquivos = baixar_arquivos_s3()
documentos, embeddings = carregar_dados(arquivos)

print("🔍 Iniciando a indexação no Chroma...")
indexar_no_chroma(documentos, embeddings)