# chat/tests/core/test_aws_integration.py
import logging
from chat.core.pdf_processing import process_all_pdfs_from_s3, process_pdf_from_s3
from chat.utils.aws_clients import s3_client

print(s3_client.list_objects(Bucket="consultor-juridico", Prefix="juridicos/"))

# Configuração
TEST_BUCKET = "consultor-juridico"
TEST_PREFIX = "juridicos/ARE1467492/agravo/"
TEST_FILE = "38-agravo.pdf"


def run_tests():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("🚀 Iniciando testes de processamento de PDFs")
    logging.info("Iniciando teste real com AWS S3")

    # Teste 1: Processamento de um PDF específico
    try:
        logging.info(f"\n\n=== TESTE 1: Processando {TEST_FILE} ===")
        docs = process_pdf_from_s3(TEST_BUCKET, f"{TEST_PREFIX}{TEST_FILE}")

        print(f"✅ Documentos processados: {len(docs)}")
        if docs:
            print("📝 Metadados do primeiro chunk:")
            print(f" - Fonte: {docs[0].metadata['source']}")
            print(f" - Página: {docs[0].metadata['page']}")
            print(f" - Tipo: {docs[0].metadata['doc_type']}")
            print(f" - Texto inicial: {docs[0].page_content[:100]}...")

    except Exception as e:
        print(f"❌ Falha no teste 1: {str(e)}")

    # Teste 2: Processamento em lote (prefix)
    try:
        logging.info(
            f"\n\n=== TESTE 2: Processando todos PDFs em {TEST_PREFIX} ===")
        all_docs = process_all_pdfs_from_s3(TEST_BUCKET, TEST_PREFIX)
        print(f"✅ Total de chunks gerados: {len(all_docs)}")
    except Exception as e:
        print(f"❌ Falha no teste 2: {str(e)}")

    # Teste 3: Arquivo inexistente
    try:
        logging.info("\n\n=== TESTE 3: Arquivo inexistente ===")
        invalid_docs = process_pdf_from_s3(TEST_BUCKET, "nao-existe.pdf")
        print(
            f"✅ Comportamento esperado: {len(invalid_docs)} documentos (deveria ser 0)")
    except Exception as e:
        print(f"❌ ERRO inesperado: {str(e)}")


def test_processamento_recursivo():
    try:
        logging.info("\n=== TESTE 4: Processamento recursivo ===")
        docs = process_all_pdfs_from_s3("consultor-juridico", "juridicos/")
        total_pdfs = len(set(d.metadata['pdf_key'] for d in docs))
        print(f"✅ PDFs processados: {total_pdfs} | Total chunks: {len(docs)}")
    except Exception as e:
        print(f"❌ Falha: {str(e)}")


if __name__ == "__main__":
    # run_tests()
    test_processamento_recursivo()


# PYTHONPATH=. python chat/tests/core/test_aws_integration.py
# ou
# PYTHONPATH=. python -m chat.tests.core.test_aws_integration
