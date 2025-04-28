from flask import request, jsonify
import os, sys

# ⬇️ Adiciona o caminho src para os imports funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importações dos serviços
from services.retrieval_and_generation.rag_service import RAGService
from services.llm_service import LLMService
from services.retrieval_and_generation.vector_search_service import VectorSearchService

from repository.chromaDB_repo import ChromaRepository


from config import Config


from src.services.llm_service import LLMService
from src.services.indexing.embedding_service import EmbeddingService
from src.services.retrieval_and_generation.vector_search_service import VectorSearchService
from src.services.retrieval_and_generation.rag_service import RAGService
from src.repository.chromaDB_repo import ChromaRepository
# Instanciações
s3_client, bedrock_client = Config.get_aws_clients()

embedding_service = EmbeddingService(
    bedrock_client=bedrock_client,
    model_id=Config.EMBEDDING_MODEL_ID
)
    
chroma_repository = ChromaRepository(
    embedding_function=embedding_service.get_embeddings(),
    collection_name=Config.CHROMA_COLLECTION,
    chroma_path=Config.CHROMA_LOCAL_PATH
)

vector_search_service = VectorSearchService(
    chroma_repository=chroma_repository,
    embedding_service=embedding_service
)

llm_service = LLMService(
    bedrock_client=bedrock_client
)

rag_service = RAGService(
    vector_search_service=vector_search_service,
    llm_service=llm_service,
    max_context_docs=Config.MAX_CONTEXT_DOCS
)

def Main():
    return "🧠 API RAG rodando"

def ProcessQuery():
    data = request.get_json()
    query = data.get("query", "")
    chat_history = data.get("chat_history", [])

    if not query:
        return jsonify({"error": "query is required"}), 400

    result = rag_service.process_query(query, chat_history)
    return jsonify(result)


