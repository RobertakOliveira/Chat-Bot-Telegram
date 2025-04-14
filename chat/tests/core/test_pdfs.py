from chat.core.pdf_processing_copy import process_pdf_from_s3, process_all_pdfs_in_bucket


def test_single_pdf():
    # Teste com um PDF específico
    bucket = "consultor-juridico"
    # Substitua por um arquivo real 16-acordao-recorrido.pdf
    key = "78-agravo.pdf"

    documents = process_pdf_from_s3(bucket, key)

    print(f"\n📊 Total de chunks gerados: {len(documents)}")
    print("\n📝 Metadados do primeiro chunk:")
    print(documents[0].metadata)

    print("\nTexto do primeiro chunk (início):")
    print(documents[0].page_content[:500] + "...")


def test_all_pdfs():
    # Teste com todos os PDFs no bucket
    bucket = "consultor-juridico"
    all_docs = process_all_pdfs_in_bucket(bucket)

    print(f"\n📊 Total de documentos processados: {len(all_docs)}")

    # Exibir estatísticas básicas
    from collections import defaultdict
    doc_types = defaultdict(int)

    for doc in all_docs:
        doc_types[doc.metadata.get('doc_subtype', 'outros')] += 1

    print("\n📈 Distribuição de tipos documentais:")
    for doc_type, count in doc_types.items():
        print(f"- {doc_type}: {count}")


if __name__ == "__main__":
    # print("=== TESTE DE PDF ÚNICO ===")
    # test_single_pdf()

    print("\n=== TESTE DE TODOS OS PDFs ===")
    test_all_pdfs()

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_pdfs
