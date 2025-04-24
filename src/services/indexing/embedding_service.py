import logging
import time
import uuid
from langchain_aws import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger("embedding_service")

class EmbeddingService:
    def __init__(self, bedrock_client, model_id, chunk_size=1000, chunk_overlap=100):
        """
        Inicializa o serviço de embeddings
        
        Args:
            bedrock_client: Cliente boto3 para Bedrock
            model_id: ID do modelo de embedding
            chunk_size: Tamanho dos chunks para divisão de texto
            chunk_overlap: Sobreposição entre chunks
        """
        self.embeddings = BedrockEmbeddings(
            client=bedrock_client,
            model_id=model_id
        )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.debug(f"Modelo de embeddings inicializado: {model_id}")
    
    def get_embeddings(self):
        """
        Retorna o objeto de embeddings configurado
        """
        return self.embeddings
    
    def split_documents(self, documents):
        """
        Divide documentos em chunks menores
        
        Args:
            documents: Lista de documentos para dividir
            
        Returns:
            list: Lista com os documentos divididos
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        splits = text_splitter.split_documents(documents)
        logger.debug(f"Documento dividido em {len(splits)} chunks")
        return splits
    
    def embed_query(self, query):
        """
        Gera embedding para uma query
        
        Args:
            query: Texto da query
            
        Returns:
            list: Vetor de embedding
        """
        embedding_start = time.time()
        query_embedding = self.embeddings.embed_query(query)
        embedding_time = time.time() - embedding_start
        logger.debug(f"Embedding gerado em {embedding_time:.4f}s (dimensões: {len(query_embedding)})")
        return query_embedding 