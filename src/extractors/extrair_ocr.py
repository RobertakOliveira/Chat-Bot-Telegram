import os
import boto3
from botocore.exceptions import ClientError
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

# Configurações
dataset_dir = "../../dataset/"
output_dir = "../textos_extraidos/"

# Nome do bucket S3 e perfil AWS
bucket_name = os.getenv("BUCKET_NAME")
session = boto3.Session(profile_name=os.getenv("AWS_PROFILE"))
s3 = session.client("s3")

# Garante que a pasta de saída local exista
os.makedirs(output_dir, exist_ok=True)

def extrair_texto_pdf(filepath):
    """Tenta extrair texto diretamente de um PDF."""
    try:
        reader = PdfReader(filepath)
        texto_extraido = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texto_extraido += page_text
        return texto_extraido.strip()
    except Exception as e:
        print(f"⚠️ Erro ao extrair texto do PDF '{filepath}': {e}")
        return ""

def aplicar_ocr_em_pdf(filepath):
    """Aplica OCR nas páginas do PDF."""
    try:
        pages = convert_from_path(filepath, dpi=300)
        texto = ""
        for idx, page_image in enumerate(pages):
            print(f"    🔎 Aplicando OCR na página {idx + 1}/{len(pages)}")
            texto += pytesseract.image_to_string(page_image, lang="por")  # OCR em português
        return texto.strip()
    except Exception as e:
        print(f"❌ Erro no OCR do PDF '{filepath}': {e}")
        return ""

def salvar_texto_local(texto, nome_arquivo):
    """Salva o texto extraído em um arquivo .txt localmente."""
    caminho_saida = os.path.join(output_dir, nome_arquivo)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"✅ Texto salvo localmente em: {caminho_saida}")
    return caminho_saida

def upload_texto_s3(caminho_arquivo_local, nome_arquivo_txt):
    """Faz upload do arquivo .txt para o S3 dentro da pasta 'textos_extraidos/'."""
    key_s3 = f"textos_extraidos/{nome_arquivo_txt}"  # Pasta dentro do bucket
    try:
        s3.upload_file(caminho_arquivo_local, bucket_name, key_s3)
        print(f"✅ Upload para S3 feito: s3://{bucket_name}/{key_s3}")
    except ClientError as e:
        print(f"❌ Erro no upload para o S3: {e}")

def processar_pdfs(caminho):
    """Processa todos os PDFs da pasta."""
    print("------------------------------------------------------")
    print(f"🔄 Procurando PDFs para extrair texto em '{caminho}'...")
    for root, dirs, files in os.walk(caminho):
        for arquivo in files:
            if arquivo.lower().endswith(".pdf"):
                filepath = os.path.join(root, arquivo)
                filepath = filepath.replace("\\", "/")

                print(f"📄 Processando PDF: {arquivo}")

                # Primeiro tenta extrair texto direto
                texto_extraido = extrair_texto_pdf(filepath)

                if not texto_extraido or len(texto_extraido) < 50:
                    print("⚠️ Texto direto do PDF vazio ou pequeno. Aplicando OCR...")
                    texto_extraido = aplicar_ocr_em_pdf(filepath)

                if texto_extraido:
                    nome_txt = os.path.splitext(arquivo)[0] + ".txt"
                    caminho_local = salvar_texto_local(texto_extraido, nome_txt)
                    upload_texto_s3(caminho_local, nome_txt)
                else:
                    print(f"❌ Nenhum texto extraído de '{arquivo}'.")

def main():
    processar_pdfs(dataset_dir)
    print("------------------------------------------------------")
    print(f"✅ Extração de texto e upload finalizados.")

if __name__ == "__main__":
    main()
