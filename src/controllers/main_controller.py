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

from langchain.chains.conversation.memory import ConversationSummaryBufferMemory
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import trim_messages
from typing_extensions import TypedDict
from typing import Annotated

# Instanciações
_, bedrock_client, _ = Config.get_aws_clients()

embedding_service = EmbeddingService(
    bedrock_client=bedrock_client,
    model_id=Config.EMBEDDING_MODEL_ID
)
    
chroma_repository = ChromaRepository(
    embedding_function=embedding_service.get_embeddings(),
    collection_name=Config.CHROMA_COLLECTION,
    chroma_path="../"+Config.CHROMA_LOCAL_PATH
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
    query = data.get("query", None)
    chat_id = data.get("chat_id", None)

    if query is None:
        return jsonify({"error": "query is required"}), 400
    elif chat_id is None:
        return jsonify({"error": "chat_id is required"}), 400

    result = rag_service.process_query(query, chat_id)
    return jsonify(result)


