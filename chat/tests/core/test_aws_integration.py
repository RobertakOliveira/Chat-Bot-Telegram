# chat/tests/core/test_aws_integration.py
from chat.core.pdf_processing import process_all_pdfs_in_bucket, process_pdf_from_s3
from chat.utils.logger import get_logger

logger = get_logger("test_aws_integration")

# 1. Configuração do Teste (ajuste conforme necessário)
TEST_BUCKET = "consultor-juridico"  # Altere para seu bucket real
TEST_PREFIX = "juridicos/"  # Prefixo para buscar PDFs
TEST_FILE = "38-agravo.pdf"


def run_tests():

    logger.info("🚀 Iniciando testes de processamento de PDFs")
    logger.info("Iniciando teste real com AWS S3")

    # Teste 1: Processamento de um PDF específico
    try:
        logger.info(f"\n\n=== TESTE 1: Processando {TEST_FILE} ===")
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
        logger.info(
            f"\n\n=== TESTE 2: Processando todos PDFs em {TEST_PREFIX} ===")
        all_docs = process_all_pdfs_in_bucket(TEST_BUCKET)
        print(f"✅ Total de chunks gerados: {len(all_docs)}")
    except Exception as e:
        print(f"❌ Falha no teste 2: {str(e)}")

    # Teste 3: Arquivo inexistente
    try:
        logger.info("\n\n=== TESTE 3: Arquivo inexistente ===")
        invalid_docs = process_pdf_from_s3(TEST_BUCKET, "nao-existe.pdf")
        print(
            f"✅ Comportamento esperado: {len(invalid_docs)} documentos (deveria ser 0)")
    except Exception as e:
        print(f"❌ ERRO inesperado: {str(e)}")


def test_processamento_recursivo():
    try:
        logger.info("\n=== TESTE 4: Processamento recursivo ===")
        docs = process_all_pdfs_in_bucket("consultor-juridico")

        total_pdfs = len(set(d.metadata['source'] for d in docs))
        print(f"✅ PDFs processados: {total_pdfs} | Total chunks: {len(docs)}")
    except Exception as e:
        print(f"❌ Falha: {str(e)}")


if __name__ == "__main__":
    run_tests()
    # test_processamento_recursivo()


# PYTHONPATH=. python chat/tests/core/test_aws_integration.py
# ou
#  python -m chat.tests.core.test_aws_integration
