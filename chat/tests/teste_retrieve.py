# chat/scripts/teste_retrieve.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.core.rag_flow import RAGFlow
from chat.utils.logger import get_logger

logger = get_logger("test_retrieve")

def test_rag_flow():
    try:
        logger.info("Iniciando teste do RAGFlow")
        
        # Inicializa com o nome da coleção explícito
        rag = RAGFlow(collection_name="collection_docs")
        
        # Exemplos de queries e filtros
        queries = [
            "BATATA"
        ]
        
        doc_type = None
        case_id = "RE1463299"
        
        for query in queries:
            print(f"\n=== Query: '{query}' ===")
            results = rag.retrieve(query, doc_type=doc_type, case_id=case_id)
            
            print(f"Documentos encontrados: {len(results)}")
            for i, doc in enumerate(results, 1):
                print(f"\nDocumento {i}:")
                print(f"Score: {doc['score']}")
                print(f"Conteúdo: {doc['content']}...")  # Mostra início do conteúdo
                if doc['metadata']:
                    print(f"Metadados: {doc['metadata']}")
    
    except Exception as e:
        logger.error(f"Erro no teste: {str(e)}")
        raise

if __name__ == "__main__":
    test_rag_flow()
