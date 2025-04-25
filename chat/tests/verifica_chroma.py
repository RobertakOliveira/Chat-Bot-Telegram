# chat/scripts/verifica_chroma.py

"""
📌 Como executar:
python chat/scripts/verifica_chroma.py --collection collection_xxxxx

👉 Para ver os embeddings também:
python chat/scripts/verifica_chroma.py --collection collection_xxxxx --embedding
"""

import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chat.core.vector_store import initialize_chroma_instance

def verificar_conteudo_chroma(collection_name, mostrar_embedding=False):
    chroma = initialize_chroma_instance(collection_name)

    print(f"\n📦 Coleção: {collection_name}")

    include_fields = ["documents", "metadatas", "embeddings"] if mostrar_embedding else ["documents", "metadatas"]
    docs = chroma.get(include=include_fields)

    print(f"🔍 Total de documentos encontrados: {len(docs['ids'])}")

    for i in range(len(docs['ids'])):
        print("\n--- Documento ---")
        print(f"🆔 ID: {docs['ids'][i]}")
        print(f"📄 Texto: {docs['documents'][i][:300]}...") # Mostra apenas 300 caracteres
        print(f"🧠 Metadata: {docs['metadatas'][i]}")
        if mostrar_embedding:
            emb = docs['embeddings'][i]
            print(f"📈 Embedding (tamanho {len(emb)}): {emb[:5]}...")  # Mostra só os 5 primeiros valores p/ não poluir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verifica documentos armazenados no ChromaDB.")
    parser.add_argument("--collection", required=True, help="Nome da coleção a ser verificada.")
    parser.add_argument("--embedding", action="store_true", help="Exibir embeddings dos documentos.")
    args = parser.parse_args()

    verificar_conteudo_chroma(args.collection, mostrar_embedding=args.embedding)