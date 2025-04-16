# Teste seu fluxo completo localmente
from chat.core.pdf_processing import process_pdf_from_s3
from chat.core.bedrock_embeddings import initialize_embedding_service

# 1. Processar PDF
docs = process_pdf_from_s3(
    "consultor-juridico",
    "juridicos/38-agravo.pdf"
)

# 2. Inicializar serviço de embeddings
embedder = initialize_embedding_service()

# 3. Gerar embeddings com nova implementação
try:
    embedded_docs = embedder.embed_documents(docs)

    # 4. Verificar saída
    if embedded_docs:
        print("=== Metadados do Primeiro Chunk ===")
        print(f"Tipo Documento: {embedded_docs[0].metadata['doc_type']}")
        print(f"Página: {embedded_docs[0].metadata['page']}")
        print(f"Modelo: {embedded_docs[0].metadata['embedding_model']}")
        print(f"Timestamp: {embedded_docs[0].metadata['embedding_timestamp']}")
        print(f"Dimensões: {len(embedded_docs[0].metadata['embedding'])}")
        print(
            f"Trecho Embedding: {embedded_docs[0].metadata['embedding'][:3]}...")

        print("\n=== Estatísticas ===")
        success = sum(1 for d in embedded_docs if d.metadata.get(
            'embedding_status') != 'failed')
        print(f"Chunks processados: {len(embedded_docs)}")
        print(f"Sucesso: {success}")
        print(f"Falhas: {len(embedded_docs) - success}")

except Exception as e:
    print(f"Erro no processo de embedding: {str(e)}")

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_embedding
