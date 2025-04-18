import os
import boto3
from botocore.exceptions import ClientError
from langchain_community.document_loaders import PyPDFLoader

# Nome do bucket S3 que será utilizado (deve ser único globalmente na AWS)
bucket_name = "meu-bucket-pdfs-eich-1407-pb-jan"

# Caminho local onde estão os arquivos PDF
dataset_dir = "dataset/"

# Nome do perfil configurado com aws configure sso
session = boto3.Session(profile_name="eich-fernandes")

# Inicializa o cliente do serviço S3 usando as credenciais configuradas no ambiente
s3 = session.client("s3")

def criar_bucket(bucket_name):
    # Verifica se o bucket já existe. Se não existir, cria um novo bucket com o nome especificado.
    print("------------------------------------------------------")
    print(f"🔄 Verificando integridade da bucket '{bucket_name}'.")
    try:
        # Tenta obter informações do bucket
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' existe.")
    except ClientError as e:
        # Se o bucket não existir ou houver erro de permissão, tenta criar
        print(f"🔄 Criando bucket '{bucket_name}'...")
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' criado com sucesso.")
        except:
            print(f"Erro inesperado: {e}")

def carregar_pdfs(caminho):
    # Percorre todos os arquivos PDF em todas as subpastas da pasta especificada
    pdfs = []
    print("------------------------------------------------------")
    print(f"🔄 Procurando arquivos PDF em '{caminho}' (incluindo subpastas).")
    for root, dirs, files in os.walk(caminho):
        for arquivo in files:
            if arquivo.endswith(".pdf"):
                full_path = os.path.join(root, arquivo)
                full_path = full_path.replace("\\","/")
                print(f"    🔄 Carregando: {full_path}")
                loader = PyPDFLoader(full_path)
                pdfs.append((full_path, loader))
    if not pdfs:
        print("❌ Nenhum arquivo PDF encontrado.")
    return pdfs

def fazer_upload(arquivos):
    print("------------------------------------------------------")
    print(f"🔄 Enviando arquivos para S3.")
    # Envia os arquivos PDF carregados para o bucket S3 especificado.
    for caminho_completo, _ in arquivos:
        # Remover subpastas do nome relativo.
        nome_relativo = caminho_completo.split("/")[-1]
        print(f"    ⬆️  Enviando '{nome_relativo}' para o bucket...")
        # Realiza upload do arquivo local para a bucket
        s3.upload_file(caminho_completo, bucket_name, nome_relativo)
        print(f"    ✅ '{nome_relativo}' enviado com sucesso!")
    print(f"✅ Arquivo(s) enviado(s) com sucesso!")

def main():
    """
    Função principal:
    - Garante que o bucket exista
    - Carrega os PDFs da pasta local
    - Realiza o upload dos arquivos para o S3
    """
    criar_bucket(bucket_name)
    arquivos_pdf = carregar_pdfs(dataset_dir)
    fazer_upload(arquivos_pdf)
    print("------------------------------------------------------")
    print(f"✅ Script encerrado.\n")

# Ponto de entrada do script
if __name__ == "__main__":
    main()
