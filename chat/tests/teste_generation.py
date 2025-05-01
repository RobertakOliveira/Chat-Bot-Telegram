# chat/scripts/teste_generation.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.scripts.rag_flow import RAGFlow
from chat.utils.logger import get_logger

logger = get_logger("test_generation")

def test_rag_generation():
    try:
        logger.info("Iniciando teste de geração com RAGFlow")

        # Inicializa com o nome da coleção explícito
        rag = RAGFlow(collection_name="collection_docs")

        # Exemplos de queries e filtros
        queries = [
            "Qual o assunto do agravo?"
        ]
        
        doc_type = "Agravo"
        case_id = "ARE1467492"
        
        for query in queries:
            print(f"\n=== Query: '{query}' ===")
            
            # Passo 1: Recupera documentos e gera a resposta
            response = rag.retrieve(query, doc_type=doc_type, case_id=case_id)
            
            print(f"Resposta gerada: {response}")
    
    except Exception as e:
        logger.error(f"Erro no teste de geração: {str(e)}")
        raise

if __name__ == "__main__":
    test_rag_generation()