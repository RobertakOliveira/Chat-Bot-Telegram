# Teste local rápido
from chat.core.pdf_processing import process_all_pdfs_in_bucket
import time

start = time.time()
BUCKET_NAME = "consultor-juridico"  # Inserir o nome do bucket aqui

docs = process_all_pdfs_in_bucket(BUCKET_NAME)
print(f" 🗂️ Bucket: {BUCKET_NAME}")

for doc in docs[:5]:  # Exibe os 5 primeiros documentos processados
    print(doc.metadata)
print(f"\n\n\n\n\n")
print(f"📊 Total de chunks gerados: {len(docs)}")
print(f"⏳ Tempo processamento: {time.time() - start:.2f}s")
print(f"📝 Metadados: {len(docs[0].metadata)} ")  # Verifique os metadados
print(f"\n📚 Total de documentos processados: {len(docs)}")

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_local_process_copy
