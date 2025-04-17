# Teste seu fluxo completo localmente
import json
from chat.core.pdf_processing import process_pdf_from_s3
from chat.core.bedrock_embeddings import initialize_embedding_service


def main():
    # 1) Carrega e processa PDF do S3 em chunks
    docs = process_pdf_from_s3(
        "consultor-juridico",
        "juridicos/38-agravo.pdf"
    )

    print(f"→ Extraídos {len(docs)} chunks.")

    # 2) Inicializa o serviço de embeddings
    embedder = initialize_embedding_service()

    # 3. Gerar embeddings com nova implementação
    try:
        embedded_docs = embedder.process_documents(docs)

        print(f"→ Gerados embeddings para {len(embedded_docs)} chunks.\n")

        # 4) Inspeciona o primeiro resultado
        first = embedded_docs[0]
        meta = first["metadata"]
        vec = first["embedding"]

        print("=== Metadados do Primeiro Chunk ===")
        print(f"ID do chunk : {first['id']}")
        print(f"Página       : {meta.get('page')}")
        print(f"Dimensões    : {len(vec)}")
        print(f"Valores iniciais: {vec[:3]}…")

        # 5) Estatísticas de sucesso/falha
        total = len(embedded_docs)
        success = sum(1 for d in embedded_docs if d.get("error") is None)
        fail = total - success
        print("\n=== Estatísticas ===")
        print(f"Chunks processados: {total}")
        print(f"Sucesso : {success}")
        print(f"Falhas  : {fail}")

        # 6) (Opcional) Salvar em JSON
        with open("output_embeddings.json", "w", encoding="utf-8") as f:
            json.dump(embedded_docs, f, ensure_ascii=False, indent=2)
        print("\nResultados salvos em output_embeddings.json")

    except Exception as e:
        print(f"Erro no processo de embedding: {e}")


if __name__ == "__main__":
    main()
# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_embedding
