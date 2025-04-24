import os
import logging
import chromadb
from langchain_chroma import Chroma

logger = logging.getLogger("chroma_repository")

class ChromaRepository:
    def __init__(self, embedding_function, collection_name, chroma_path):
        """
        Inicializa o repositório ChromaDB
        
        Args:
            embedding_function: Função de embedding a ser usada
            collection_name: Nome da coleção no ChromaDB
            chroma_path: Caminho para o diretório do ChromaDB
        """
        self.embedding_function = embedding_function
        self.collection_name = collection_name
        self.chroma_path = chroma_path
        
        if not os.path.exists(chroma_path):
            os.makedirs(chroma_path, exist_ok=True)
            logger.info(f"Diretório ChromaDB criado: {chroma_path}")
    
    def get_vectorstore(self):
        """
        Carrega e retorna o vectorstore do ChromaDB
        """
        logger.debug(f"Carregando ChromaDB de: {self.chroma_path}")
        load_start = __import__('time').time()
        
        chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        vectorstore = Chroma(
            client=chroma_client,
            embedding_function=self.embedding_function,
            collection_name=self.collection_name
        )
        
        load_time = __import__('time').time() - load_start
        logger.info(f"✅ ChromaDB carregado com sucesso em {load_time:.4f}s")
        
        return vectorstore
    
    def add_documents(self, documents):
        """
        Adiciona documentos ao ChromaDB
        
        Args:
            documents: Lista de documentos para adicionar
        """
        vectorstore = self.get_vectorstore()
        vectorstore.add_documents(documents)
        logger.info(f"✅ {len(documents)} documentos adicionados ao ChromaDB") 