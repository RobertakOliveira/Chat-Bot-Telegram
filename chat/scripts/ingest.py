# chat/scripts/ingest.py

import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chat.core.pdf_processing import process_pdf_from_s3, list_pdfs_in_bucket
from chat.core.vector_store import initialize_chroma_instance
from chat.utils.config import config
from chat.utils.logger import get_logger

# Inicializa o logger específico para o processo de ingestão
logger = get_logger("ingest")
# Define o número máximo de threads para processamento paralelo
MAX_WORKERS = 4

def ingest_pdfs(bucket_name: str, collection_name: str):
    """Processa todos os PDFs do bucket S3 e indexa no ChromaDB."""
    logger.info(f"🚀 Iniciando ingestão do bucket: {bucket_name}")
    start_total = time.time() # Marca o tempo inicial para cálculo da duração total do processo

    try:
        # Obtém lista de todos os arquivos PDF disponíveis no bucket S3
        pdf_files = list_pdfs_in_bucket(bucket_name)
        logger.info(f"📄 Total de PDFs encontrados: {len(pdf_files)}")

        # Inicializa a instância do ChromaDB com o nome da coleção especificada
        chroma = initialize_chroma_instance(collection_name)
        # Lista que armazenará todos os documentos processados
        all_docs = []

        def process_single_pdf(pdf):
            """
            Função interna para processar um único arquivo PDF
            Retorna uma lista de documentos/chunks extraídos do PDF
            """
            start = time.time()
            logger.info(f"🔍 Processando: {pdf['key']}")

            # Chama a função que extrai o conteúdo do PDF do S3 e o divide em chunks
            docs = process_pdf_from_s3(pdf['bucket'], pdf['key'])
            # Verifica se algum conteúdo foi extraído
            if not docs:
                logger.warning(f"⚠️ Nenhum conteúdo extraído de {pdf['key']}")
                return []

            # Extrai o ID do caso a partir do caminho do arquivo
            # Assume que o padrão do caminho é algo como "pasta/case_id/arquivo.pdf"
            case_id = pdf['key'].split("/")[1]

            for doc in docs:
                # Garante que metadata seja um dicionário
                if not isinstance(doc.metadata, dict):
                    doc.metadata = {}
                # Define o tipo de documento como "document", se não estiver definido
                doc.metadata.setdefault("_type", "document")
                # Adiciona o ID do caso como metadado
                doc.metadata["case_id"] = case_id

            # Calcula e registra a duração do processamento deste PDF
            duration = time.time() - start
            logger.info(f"✔️ {pdf['key']} → {len(docs)} chunks em {duration:.2f}s")
            return docs

        # Inicia o processamento paralelo dos PDFs usando ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Cria e submete tarefas para cada PDF encontrado
            futures = [executor.submit(process_single_pdf, pdf) for pdf in pdf_files]
            # Coleta os resultados à medida que são concluídos
            for future in as_completed(futures):
                docs = future.result()
                all_docs.extend(docs)  # Adiciona os documentos processados à lista principal

        # Verifica se há documentos para indexar
        if all_docs:
            logger.info(f"🧠 Gerando embeddings para {len(all_docs)} documentos...")
            # Adiciona todos os documentos processados ao ChromaDB, que gerará embeddings
            chroma.add_documents(documents=all_docs)
            logger.info(f"✅ Indexação concluída na coleção '{collection_name}' com {len(all_docs)} docs.")
        else:
            logger.warning("⚠️ Nenhum documento válido para indexar.")

        # Registra o tempo total do processo de ingestão
        logger.info(f"🏁 Ingestão finalizada em {time.time() - start_total:.2f} segundos")
        
    except Exception as e:
        # Captura e registra qualquer erro durante o processo
        logger.error(f"🔥 Falha crítica: {str(e)}")
        # Propaga a exceção para tratamento em nível superior
        raise

# Ponto de entrada para execução direta do script
if __name__ == "__main__":
    logger.info("🛠️ Iniciando ingestão de PDFs...")
    collection_name = "collection_docs" # Define o nome padronizado da coleção no ChromaDB
    print(f"Nome da coleção gerado: {collection_name}")
    ingest_pdfs(config.S3_BUCKET_NAME, collection_name) # Inicia o processo de ingestão com o nome do bucket do S3 definido na configuração