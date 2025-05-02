import sys
import os
from typing import Optional
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Rag.JusBot import JusBotRAG


rag_system = JusBotRAG()

def listar_documentos_rag():
    return rag_system.listar_documentos()

def consultar_rag(pergunta: str, documento: Optional[str] = None) -> str:
    return rag_system.query_document(pergunta, documento)
