# chat/tests/core/test_full_pipeline.py
import tempfile
from langchain_community.vectorstores import Chroma
from chat.core.pdf_processing import process_pdf_from_s3
from chat.core.bedrock_embeddings import BedrockEmbeddingHandler
from chat.core.query_embeddings import get_query_embedding
from langchain_core.documents import Document
from chat.utils.logger import logger

# Configurações de teste
BUCKET_NAME = "consultor-juridico"
TEST_PDF_KEY = "juridicos/38-agravo.pdf"
TEMPDIR = tempfile.mkdtemp()


def test_full_pipeline():
    print("\n🔍 Iniciando teste completo do pipeline jurídico...")

    try:
        # 1. Processamento do PDF
        print("\n📥 Etapa 1: Download e processamento do PDF...")
        documents = process_pdf_from_s3(BUCKET_NAME, TEST_PDF_KEY)

        if not documents:
            raise ValueError("Nenhum documento processado")

        print(f"✅ {len(documents)} chunks gerados com sucesso")

        # 2. Geração de embeddings
        print("\n🧠 Etapa 2: Gerando embeddings...")
        embedder = BedrockEmbeddingHandler()
        embeddings_data = embedder.process_documents(documents)

        if not embeddings_data:
            raise ValueError("Falha na geração de embeddings")

        print(f"✅ {len(embeddings_data)} embeddings gerados")

        # 3. Criação do ChromaDB
        print("\n🗄️ Etapa 3: Criando vetorstore no ChromaDB...")
        # TODO: Substituir por implementação oficial do Chroma quando disponível
        # ------------------------------------------------------------
        # ATENÇÃO: Esta é uma implementação básica temporária do Chroma
        # que será substituída pela versão oficial do módulo de vetorização
        # ------------------------------------------------------------
        vector_db = Chroma.from_documents(
            documents=[Document(page_content=item['text'], metadata=item['metadata'])
                       for item in embeddings_data],
            embedding=embedder.embeddings,
            persist_directory=TEMPDIR
        )
        print(f"✅ ChromaDB temporário criado em: {TEMPDIR}")

        # 4. Teste de consultas
        print("\n🔎 Etapa 4: Testando consultas jurídicas...")
        # TODO: Migrar para a interface oficial de consultas quando disponível
        # ------------------------------------------------------------
        # NOTA: Esta consulta direta ao Chroma será substituída pela camada
        # de abstração do módulo oficial de vector store
        # ------------------------------------------------------------
        test_queries = [
            "Qual o fundamento legal do agravo?",
            "Quem é o relator do caso?",
            "Qual foi a decisão proferida?"
        ]

        for query in test_queries:
            print(f"\n💡 Consulta: '{query}'")

            # Gera embedding da pergunta
            query_embedding = get_query_embedding(query)

            # Busca no ChromaDB
            results = vector_db.similarity_search_by_vector(
                query_embedding, k=1)

            if results:
                doc = results[0]
                print(
                    f"📌 Documento relevante (página {doc.metadata['page']}):")
                print(doc.page_content[:300] + "...")
            else:
                print("⚠️ Nenhum resultado encontrado")

        print("\n🎉 Teste concluído com sucesso!")

    except Exception as e:
        logger.error(f"❌ Falha no teste: {str(e)}")
        raise


if __name__ == "__main__":
    test_full_pipeline()

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_full_pipeline
