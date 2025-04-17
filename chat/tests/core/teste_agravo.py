import tempfile
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from chat.utils.aws_clients import s3_client, bedrock_runtime
import re

# Configurações
BUCKET_NAME = "consultor-juridico"
PDF_KEY = "juridicos/38-agravo.pdf"
TEMPDIR = tempfile.mkdtemp()
# Em produção, defina um path fixo (ex: /data/chroma_db)

print("🔍 Iniciando teste com o agravo de instrumento direto ao S3....")

# 1. Download do PDF


def download_from_s3(bucket, key):
    """Download robusto com tratamento de erros"""
    try:
        # Verifica se o arquivo existe
        s3_client.head_object(Bucket=bucket, Key=key)

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            s3_client.download_fileobj(bucket, key, tmp_file)
            print(f"✅ Download concluído: s3://{bucket}/{key}")
            return tmp_file.name

    except Exception as e:
        print(f"❌ Erro crítico no download:")
        print(f"- Tipo: {type(e).__name__}")
        print(f"- Mensagem: {str(e)}")
        print("\nVerifique:")
        print(f"1. Se o arquivo existe: aws s3 ls s3://{bucket}/{key}")
        print("2. Suas permissões AWS com: aws sts get-caller-identity")
        print("3. Se a região está correta (us-east-1)")
        exit()


print(f"📥 Baixando {PDF_KEY} do S3...")
local_pdf = download_from_s3(BUCKET_NAME, PDF_KEY)

# 2. Processamento Especializado para Documentos Jurídicos


def clean_legal_text(text):
    """Limpeza avançada para textos jurídicos"""
    if not text:
        return ""

    # Normalização de espaços e quebras
    text = re.sub(r'(\n\s*){2,}', '\n\n', text)  # Múltiplas quebras -> 2
    # Remove espaços antes pontuação
    text = re.sub(r'(?<=\w)\s+(?=[.,;:])', '', text)
    text = re.sub(r'(\d)\s+(?=\d)', r'\1', text)  # Junta números
    return text.strip()


print("✂️ Processando e dividindo em chunks jurídicos...")
try:
    loader = PyPDFLoader(local_pdf)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "EMENTA:",
            "ACÓRDÃO",
            "Vistos, relatados e discutidos estes autos",
            "\n",
            " ",  # Último recurso
        ]
    )

    documents = []
    for page in loader.load():
        clean_text = clean_legal_text(page.page_content)
        chunks = text_splitter.create_documents(
            [clean_text],
            [{
                "source": "38-agravo.pdf",
                "page": page.metadata["page"],
                "doc_type": "agravo"
            }]
        )
        documents.extend(chunks)
    print(f"✅ Gerados {len(documents)} chunks jurídicos")
except Exception as e:
    print(f"❌ Falha no processamento do PDF:")
    print(f"- Erro: {str(e)}")
    print("\nSoluções possíveis:")
    print("1. Verifique se o PDF não está corrompido")
    print("2. Tente outro parser: from langchain_community.document_loaders import UnstructuredPDFLoader")
    exit()

# 3. Configuração do Bedrock
print("🧠 Configurando Bedrock Titan...")
try:
    embeddings = BedrockEmbeddings(
        client=bedrock_runtime,
        model_id="amazon.titan-embed-text-v1"
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
            print(f"📌 Página {doc.metadata['page']}:")
            print(doc.page_content[:300] + "...")
            print("---")
    except Exception as e:
        print(f"⚠️ Erro na consulta: {str(e)}")

print(f"\n🎉 Teste completo! Dados persistidos em: {TEMPDIR}")

# Navegue até a pasta raiz e execute:
#     PYTHONPATH =. python -m chat.tests.core.teste_agravo // se der erro execute somente o comando:
#     python -m chat.tests.core.teste_agravo
