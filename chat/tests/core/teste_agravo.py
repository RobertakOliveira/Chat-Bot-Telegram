import tempfile
from langchain_community.vectorstores import Chroma
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import bedrock_runtime, AWS_REGION
from chat.utils.config import bedrock_config
from chat.core.pdf_processing import process_pdf_from_s3
import re

# Configurações
BUCKET_NAME = "consultor-juridico"
PDF_KEY = "juridicos/38-agravo.pdf"
TEMPDIR = tempfile.mkdtemp()
# Em produção, defina um path fixo (ex: /data/chroma_db)

print("🔍 Iniciando teste com o agravo de instrumento direto ao S3....")

# 1. Processamento do PDF usando suas funções
print(f"📥 Processando {PDF_KEY} do S3 com suas funções personalizadas...")
try:
    documents = process_pdf_from_s3(BUCKET_NAME, PDF_KEY)

    if not documents:
        print("❌ Nenhum documento foi processado - verifique os logs para detalhes")
        exit()

    print(
        f"✅ Gerados {len(documents)} chunks dos documentos jurídicos processados")
    print(f"📝 Metadados do primeiro documento:")
    print(documents[0].metadata)
    print("---")

except Exception as e:
    print(f"❌ Falha no processamento personalizado:")
    print(f"- Erro: {str(e)}")
    exit()

# 3. Configuração do Bedrock
print("🧠 Configurando Bedrock Titan...")
try:
    embeddings = BedrockEmbeddings(
        client=bedrock_runtime,
        model_id=bedrock_config.MODEL_ID,
        region_name=AWS_REGION
    )
except Exception as e:
    print(f"❌ Falha na configuração do Bedrock:")
    print(f"- Verifique se o modelo está ativado na região us-east-1")
    print(f"- Erro completo: {str(e)}")
    exit()

# 4. Indexação no ChromaDB
print("🗄️ Criando vetorstore no ChromaDB...")
try:
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=TEMPDIR  # "/data/chroma_db"  Path fixo
    )
    print(f"✅ Vetorstore criado com {len(documents)} documentos")
except Exception as e:
    print(f"❌ Falha na criação do ChromaDB:")
    print(f"- Erro: {str(e)}")
    print("\nVerifique:")
    print("1. Se os embeddings foram gerados corretamente")
    print("2. Se há espaço em disco suficiente")
    exit()

# 5. Teste com Consultas Jurídicas
test_queries = [
    "Qual o fundamento do agravo?",
    "Quem é o relator do caso?",
    "Qual a decisão proferida?"
]

print("\n🔎 Testando consultas jurídicas:")
for query in test_queries:
    print(f"\n💡 Consulta: '{query}'")
    try:
        results = vector_db.similarity_search(query, k=1)
        for doc in results:
            print(
                f"📌 Página {doc.metadata['page']} ({doc.metadata['doc_type']}):")
            print(doc.page_content[:300] + "...")
            print("---")
    except Exception as e:
        print(f"⚠️ Erro na consulta: {str(e)}")

print(f"\n🎉 Teste completo! Dados persistidos em: {TEMPDIR}")

# Navegue até a pasta raiz e execute:
#     PYTHONPATH =. python -m chat.tests.core.teste_agravo // se der erro execute somente o comando:
#     python -m chat.tests.core.teste_agravo
