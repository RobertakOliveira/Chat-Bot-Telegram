# chat/scripts/verifica_chroma.py

import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chat.core.vector_store import initialize_chroma_instance

def verificar_conteudo_chroma(collection_name):
    chroma = initialize_chroma_instance(collection_name)

    print(f"\n📦 Coleção: {collection_name}")
    docs = chroma.get()
    print(f"🔍 Total de documentos encontrados: {len(docs['ids'])}")
    
    for i in range(len(docs['ids'])):
        print("\n--- Documento ---")
        print(f"🆔 ID: {docs['ids'][i]}")
        print(f"📄 Texto: {docs['documents'][i][:300]}...")
        print(f"🧠 Metadata: {docs['metadatas'][i]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verifica documentos armazenados no ChromaDB.")
    parser.add_argument("--collection", required=True, help="Nome da coleção a ser verificada.")
    args = parser.parse_args()

    verificar_conteudo_chroma(args.collection)