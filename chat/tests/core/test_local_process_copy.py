# Teste local rápido
from chat.core.pdf_processing_copy import process_pdf_from_s3
import time

start = time.time()

docs = process_pdf_from_s3("consultor-juridico")


print(f"📊 Total de chunks gerados: {len(docs)}")
print(f"Tempo processamento: {time.time() - start:.2f}s")
print(f"\nMetadados: {len(docs[0].metadata)} ")  # Verifique os metadados

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_local_process_copy
