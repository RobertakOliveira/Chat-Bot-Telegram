# Teste local rápido
from chat.core.pdf_processing import process_all_pdfs_in_bucket
import time


def run_test():
    start = time.time()
    BUCKET_NAME = "consultor-juridico"  # Inserir o nome do bucket aqui

    print("\n=== Iniciando Teste de Processamento ===")
    docs = process_all_pdfs_in_bucket(BUCKET_NAME)

    print(f"\n🗂️  Bucket: {BUCKET_NAME}")
    print(f"📊  Total de chunks gerados: {len(docs)}")
    print(f"⏳  Tempo processamento: {time.time() - start:.2f}s")

    if docs:
        print("\n🔍 Exemplo de Metadados:")
        for i, doc in enumerate(docs[:3]):
            print(f"Chunk {i+1}:")
            print(f"  Tipo Documento: {doc.metadata.get('doc_type')}")
            print(f"  Origem: {doc.metadata.get('source')}")
            print(f"  Página: {doc.metadata.get('page')}\n")

    for doc in docs[:5]:  # Exibe os 5 primeiros documentos processados
        print(doc.metadata)
    print(f"\n\n")

    print(f"📝 Metadados: {len(docs[0].metadata)} ")  # Verifique os metadados
    print(f"📚 Total de documentos processados: {len(docs)}")


if __name__ == "__main__":
    run_test()
# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_local_process_copy
