from chat.core.pdf_processing import process_pdf_from_s3, process_all_pdfs_in_bucket


def test_single_pdf():
    # Teste com um PDF específico
    bucket = "consultor-juridico"
    # Substitua por um arquivo real 16-acordao-recorrido.pdf
    key = "78-agravo.pdf"

    documents = process_pdf_from_s3(bucket, key)

    print(f"\n📊 Total de chunks gerados: {len(documents)}")
    print("\n📈 Metadados do primeiro chunk:")
    print(documents[0].metadata)

    print("\n📝 Texto do primeiro chunk (início):")
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


def test_all_pdfs_com_metadados():
    # Teste com todos os PDFs no bucket
    bucket = "consultor-juridico"
    all_docs = process_all_pdfs_in_bucket(bucket)

    # Nome do arquivo onde a saída será salva
    output_file = "output_documentos_processados.txt"

    print(f"\n📊 Total de documentos processados: {len(all_docs)}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"📊 Total de documentos processados: {len(all_docs)}\n\n")

        # Exibir metadados e texto de cada chunk
        for i, doc in enumerate(all_docs):
            f.write(f"📝 Chunk {i + 1}:\n")
            f.write(f"📄 Metadados: {doc.metadata}\n")
            # Exibe os primeiros 500 caracteres do texto
            f.write(f"📖 Texto (início): {doc.page_content[:500]}...\n\n")

        # Exibir estatísticas básicas
        from collections import defaultdict
        doc_types = defaultdict(int)

        for doc in all_docs:
            doc_types[doc.metadata.get('doc_subtype', 'outros')] += 1

        f.write("\n📈 Distribuição de tipos documentais:\n")
        for doc_type, count in doc_types.items():
            f.write(f"- {doc_type}: {count}\n")

        # Exibir total de chunks gerados
        total_chunks = sum(len(doc.page_content) for doc in all_docs)
        f.write(f"\n📊 Total de chunks gerados: {total_chunks}\n")

    print(f"🔍 Saída gravada em {output_file}")


if __name__ == "__main__":
    # print("=== TESTE DE PDF ÚNICO ===")
    # test_single_pdf()

    print("\n=== TESTE DE TODOS OS PDFs ===")
    test_all_pdfs()

    # print("\n=== TESTE DE TODOS OS PDFs COM METADADOS ===")
    # test_all_pdfs_com_metadados()

# Teste local rápido
# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_pdfs
