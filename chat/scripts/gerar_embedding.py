# chat/scripts/gerar_embedding.py
from chat.core.pdf_processing import generate_embeddings_for_pdfs
import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")))

# Agora, o Python deve ser capaz de importar o módulo chat


def main():
    bucket_name = "consultor-juridico"  # Nome do seu bucket S3
    prefix = "juridicos/"  # Prefixo para filtrar PDFs na pasta "juridicos"

    # Processar todos os PDFs e gerar os embeddings
    generate_embeddings_for_pdfs(bucket_name, prefix)

    print("🗂️ Embeddings gerados com sucesso!")


if __name__ == "__main__":
    main()

# A DEFINIR PADRÃO DE VARIÁVEIS DE AMBIENTE: buckets, api, etc.
# $ python -m chat.scripts.gerar_embedding
