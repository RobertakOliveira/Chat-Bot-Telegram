import json
from pathlib import Path
from collections import defaultdict
from langchain_community.document_loaders import PyPDFLoader
from chat.core.pdf_processing import process_pdf_from_s3, process_all_pdfs_in_bucket
import logging
from chat.utils.logger import get_logger

# logo no topo:
logger = get_logger("test_pdfs")
logger.setLevel(logging.DEBUG)


def test_single_pdf(bucket, key, output_file="single_pdf_chunks.txt"):
    # Processa o PDF
    documents = process_pdf_from_s3(bucket, key)

    # Exibe resumo no console (opcional)
    logger.info(
        "\n📊 Total de chunks gerados: %d\n📈 Metadados do primeiro chunk:\n%s\n📝 Texto do primeiro chunk (início):\n%s ..." % (
            len(documents),
            json.dumps(documents[0].metadata, indent=2, ensure_ascii=False),
            documents[0].page_content[:500]
        )
    )

    # Grava os chunks e metadados no arquivo de texto
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in documents:
            # Combine metadados e conteúdo em um único dicionário
            data_to_write = {
                "page_content": doc.page_content,
                "metadata": doc.metadata
            }
            # Escreve o dicionário como uma única linha JSON
            f.write(json.dumps(data_to_write, ensure_ascii=False) + "\n")

    print(f"🔍 Saída gravada em {output_file}")


def test_all_pdfs():
    # Teste com todos os PDFs no bucket
    bucket = "consultor-juridico"
    all_docs = process_all_pdfs_in_bucket(bucket)

    logger.info(f"\n📊 Total de documentos processados: {len(all_docs)}")

    # Exibir estatísticas básicas

    doc_types = defaultdict(int)

    for doc in all_docs:
        doc_types[doc.metadata.get('doc_type', 'outros')] += 1

    logger.info("\n📈 Distribuição de tipos documentais:")
    for doc_type, count in doc_types.items():
        logger.info(f"- {doc_type}: {count}")


def test_all_pdfs_com_metadados():
    # Teste com todos os PDFs no bucket
    bucket = "consultor-juridico"
    all_docs = process_all_pdfs_in_bucket(bucket)

    # Nome do arquivo onde a saída será salva
    output_file = "output_documentos_processados.txt"

    logger.info(f"\n📊 Total de documentos processados: {len(all_docs)}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"📊 Total de documentos processados: {len(all_docs)}\n\n")

        # Exibir metadados e texto de cada chunk
        for i, doc in enumerate(all_docs):
            f.write(f"📝 Chunk {i + 1}:\n")
            f.write(f"📄 Metadados: {doc.metadata}\n")
            # Exibe os primeiros 500 caracteres do texto
            f.write(f"📖 Texto (início): {doc.page_content[:500]}...\n\n")

        # Exibir estatísticas básicas

        doc_types = defaultdict(int)

        for doc in all_docs:
            doc_types[doc.metadata.get('doc_type', 'outros')] += 1

        f.write("\n📈 Distribuição de tipos documentais:\n")
        for doc_type, count in doc_types.items():
            f.write(f"- {doc_type}: {count}\n")

        # Exibir total de chunks gerados
        total_chunks = sum(len(doc.page_content) for doc in all_docs)
        f.write(f"\n📊 Total de chunks gerados: {total_chunks}\n")

    print(f"🔍 Saída gravada em {output_file}")


def test_local_pdf_page_count():
    # Teste com um PDF local (exemplo: 78-agravo.pdf)
    # Caminho absoluto robusto
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    pdf_path = base_dir / "infra" / "juridicos" / "78-agravo.pdf"

    if not pdf_path.exists():
        logger.error(f"❌ Arquivo não encontrado: {pdf_path}")
        return

    loader = PyPDFLoader(str(pdf_path), mode="page")
    docs = loader.load()

    logger.info(f"📄 Total de páginas detectadas: {len(docs)}")
    for i, doc in enumerate(docs, start=1):
        logger.info(f"📑 Página {i} → {len(doc.page_content)} caracteres")


if __name__ == "__main__":
    logger.info("=== TESTE DE PDF ÚNICO ===")

    # Configurações para o PDF que você quer testar
    bucket = "consultor-juridico-talita"  # Substitua pelo seu bucket S3
    # Substitua pela chave do seu PDF
    key = "juridicos/ARE1467492/agravo/38-agravo.pdf"
    output_file = "chunks_38_agravo.txt"  # Nome do arquivo de saída

    test_single_pdf(bucket, key, output_file)

    # test_local_pdf_page_count() # Você pode manter ou comentar este teste

    # logger.info("\n=== TESTE DE PDF ÚNICO COM CONTAGEM DE PÁGINAS ===")
    # test_local_pdf_page_count()

    # logger.info("\n=== TESTE DE TODOS OS PDFs ===")
    # test_all_pdfs()

    # logger.info("\n=== TESTE DE TODOS OS PDFs COM METADADOS ===")
    # test_all_pdfs_com_metadados()

# Teste local rápido
# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_pdfs
