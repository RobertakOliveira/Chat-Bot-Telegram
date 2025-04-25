# chat/tests/core/test_full_pipeline.py
import tempfile
from chat.core.pdf_processing import process_pdf_from_s3
from chat.core.bedrock_embeddings import BedrockEmbeddingHandler
from chat.core.vector_store import index_documents_in_chroma, initialize_chroma_instance
from chat.core.query_embeddings import get_query_embedding
from langchain_core.documents import Document
from chat.utils.logger import get_logger

logger = get_logger("test_full_pipeline")

# Configurações de teste
BUCKET_NAME = "consultor-juridico"
TEST_PDF_KEY = "juridicos/38-agravo.pdf"
COLLECTION_NAME = "test_pipeline_collection"


def test_full_pipeline():
    logger.info("\n🔍 Iniciando teste completo do pipeline jurídico...")

    try:
        # 1. Processamento do PDF
        logger.info("\n📥 Etapa 1: Download e processamento do PDF...")
        documents = process_pdf_from_s3(BUCKET_NAME, TEST_PDF_KEY)

        if not documents:
            raise ValueError("Nenhum documento processado")

        logger.info(f"✅ {len(documents)} chunks gerados com sucesso")

        # 2. Geração de embeddings e indexação
        logger.info("\n🧠 Etapa 2: Gerando embeddings e indexando...")
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        # Usando a função de ingestão da Rhafa
        index_documents_in_chroma(
            texts=texts,
            metadatas=metadatas,
            case_id="test_case",
            collection_name=COLLECTION_NAME
        )
        logger.info(f"✅ Documentos indexados na coleção '{COLLECTION_NAME}'")

        # 3. Teste de consultas
        logger.info("\n🔎 Etapa 4: Testando consultas jurídicas...")
        test_queries = [
            "Qual o fundamento legal do agravo?",
            "Quem é o relator do caso?",
            "Qual foi a decisão proferida?"
        ]

        # Inicializa a instância do Chroma
        chroma_instance = initialize_chroma_instance(COLLECTION_NAME)

        for query in test_queries:
            logger.info(f"\n💡 Consulta: '{query}'")

            # Gera embedding da pergunta
            query_embedding = get_query_embedding(query)

            # Busca no ChromaDB usando a implementação da Rhafa
            results = chroma_instance.similarity_search_by_vector(
                query_embedding, k=1)

            if results:
                doc = results[0]
                logger.info(
                    f"📌 Documento relevante (página {doc.metadata['page']}):")
                logger.info(doc.page_content[:300] + "...")
            else:
                logger.info("⚠️ Nenhum resultado encontrado")

        logger.info("\n🎉 Teste concluído com sucesso!")

    except Exception as e:
        logger.error(f"❌ Falha no teste: {str(e)}")
        raise
    finally:
        # Limpeza opcional: remover a coleção de teste após o teste
        try:
            chroma_instance.delete_collection()
            logger.info(f"🧹 Coleção '{COLLECTION_NAME}' removida")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível limpar a coleção: {str(e)}")


if __name__ == "__main__":
    test_full_pipeline()

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_full_pipeline
