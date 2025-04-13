from chat.core.pdf_processing import process_all_pdfs_from_s3
from chat.core.bedrock_embeddings import BedrockEmbeddingHandler

# Processa tudo
docs = process_all_pdfs_from_s3("consultor-juridico")
embedder = BedrockEmbeddingHandler()
embedded_docs = embedder.embed_documents(docs)

print(f"✅ {len(embedded_docs)} chunks processados!")
print(f"📄 Exemplo: {embedded_docs[0].metadata['source']}")
print(
    f"🔢 Dimensões do embedding: {len(embedded_docs[0].metadata['embedding'])}")
