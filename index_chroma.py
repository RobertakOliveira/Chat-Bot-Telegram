import os
import json
import boto3
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FakeEmbeddings

# Configurações
bucket = "grupo-7"
prefixo = "embeddings_temp/"
chroma_path = "chroma_db_producao"
os.makedirs(prefixo, exist_ok=True)

# Baixa arquivos JSON da bucket
def baixar_arquivos_s3():
    print("🔽 Baixando arquivos JSON do S3...")
    s3 = boto3.client("s3")
    arquivos = s3.list_objects_v2(Bucket=bucket).get("Contents", [])

    baixados = []
    for obj in arquivos:
        key = obj["Key"]
        if key.endswith(".json"):
            caminho_local = os.path.join(prefixo, os.path.basename(key))
            s3.download_file(bucket, key, caminho_local)
            baixados.append(caminho_local)
            print(f"✔️ Baixado: {key} → {caminho_local}")
    return baixados

# Carrega os documentos e embeddings
def carregar_dados(arquivos):
    documentos = []
    embeddings = []
    tamanho_esperado = None

    for arquivo in arquivos:
        with open(arquivo, "r") as f:
            dados = json.load(f)
            for item in dados:
                emb = item["embedding"]
                if tamanho_esperado is None:
                    tamanho_esperado = len(emb)
                documentos.append(Document(page_content=item["text"], metadata=item.get("metadata", {})))
                embeddings.append(emb)
                print(f"📏 Dimensão do embedding: {len(emb)}")

    print(f"📊 Total de embeddings válidos: {len(embeddings)}")
    return documentos, embeddings

# Embedding fake para indexação manual
class StaticEmbeddings(FakeEmbeddings):
    def __init__(self, static_embeddings):
        super().__init__(size=len(static_embeddings[0]))
        self._static_embeddings = static_embeddings

    def embed_documents(self, texts):
        return self._static_embeddings

# Indexa no Chroma
def indexar_embeddings(documentos, embeddings):
    print("📦 Indexando embeddings no Chroma...")
    modelo_falso = StaticEmbeddings(embeddings)

    db = Chroma.from_documents(
        documents=documentos,
        embedding=modelo_falso,
        persist_directory=chroma_path
    )
    db.persist()
    print("✅ Indexação finalizada.")

# Execução
if __name__ == "__main__":
    arquivos = baixar_arquivos_s3()
    documentos, embeddings = carregar_dados(arquivos)
    indexar_embeddings(documentos, embeddings)
