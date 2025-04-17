# Teste de integração
from chat.core.pdf_processing import process_all_pdfs_in_bucket
from chat.core.bedrock_embeddings import BedrockEmbeddingHandler

# Processar documentos
documents = process_all_pdfs_in_bucket("consultor-juridico")

# Gerar embeddings
handler = BedrockEmbeddingHandler()
embeddings_data = handler.process_documents(documents)

# Verificação
if embeddings_data:
    print(f"\n✅ {len(embeddings_data)} chunks processados!")

    # Acesso via dicionário
    sample = embeddings_data[0]
    print(f"📄 Origem: {sample['metadata']['source']}")     # Chave aninhada
    print(f"🔢 Dimensões: {len(sample['embedding'])}")      # Embedding direto
    print(f"🆔 ID Único: {sample['id']}")                   # ID gerado

    print(f"\n\n📄 Exemplo: {embeddings_data[0]['metadata']['source']}")
    print(f"🔢 Dimensões do embedding: {len(embeddings_data[0]['embedding'])}")
else:
    print("❌ Nenhum embedding gerado!")

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_process_embedding
