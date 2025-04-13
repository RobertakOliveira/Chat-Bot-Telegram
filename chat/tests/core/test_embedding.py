# Teste seu fluxo completo localmente
from chat.core.pdf_processing import process_pdf_from_s3
from chat.core.bedrock_embeddings import BedrockEmbeddingHandler

# 1. Processar PDF
docs = process_pdf_from_s3(
    "consultor-juridico", "juridicos/ARE1467492/agravo/38-agravo.pdf")

# 2. Gerar embeddings
embedder = BedrockEmbeddingHandler()
embedded_docs = embedder.embed_documents(docs)

# 3. Verificar saída
print(
    f"Primeiro embedding ({len(embedded_docs[0].metadata['embedding'])} dimensões):")
print(embedded_docs[0].metadata['embedding'][:5])  # Mostra primeiros valores
