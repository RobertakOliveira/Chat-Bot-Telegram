# Teste local rápido
from chat.core.pdf_processing import process_all_pdfs_in_bucket
import time
import json


def save_chunks_as_json(docs, output_file="output_chunks.json"):
    chunks_data = []
    for i, doc in enumerate(docs):
        chunk_data = {
            "chunk": i + 1,
            "doc_type": doc.metadata.get('doc_type'),
            "source": doc.metadata.get('source'),
            "page": doc.metadata.get('page'),
            "content": doc.page_content
        }
        chunks_data.append(chunk_data)

    # Salva os dados em um arquivo JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=4)
    print(f"\n🔒 Chunks salvos como .json em {output_file}")


def save_chunks_to_txt(docs, file_path="chunks_output.txt"):
    with open(file_path, "w", encoding="utf-8") as f:
        for i, doc in enumerate(docs):
            # Exibindo conteúdo do chunk
            content = doc.page_content if hasattr(
                doc, 'page_content') else "Sem conteúdo"

            # Salvando metadados e conteúdo
            f.write(f"=== Chunk {i+1} ===\n")
            f.write(
                f"Tipo Documento: {doc.metadata.get('doc_type', 'Desconhecido')}\n")
            f.write(f"Origem: {doc.metadata.get('source', 'Desconhecido')}\n")
            f.write(f"Página: {doc.metadata.get('page', 'Desconhecido')}\n")
            f.write("\nConteúdo do Chunk:\n")
            f.write(content)
            f.write("\n\n" + "="*50 + "\n\n")  # Separador entre os chunks


def run_test():
    start = time.time()
    BUCKET_NAME = "consultor-juridico"  # Inserir o nome do bucket aqui

    print("\n=== Iniciando Teste de Processamento ===")
    docs = process_all_pdfs_in_bucket(BUCKET_NAME)

    print(f"\n🗂️  Bucket: {BUCKET_NAME}")
    print(f"📊  Total de chunks gerados: {len(docs)}")
    print(f"⏳  Tempo processamento: {time.time() - start:.2f}s")

    if docs:
        print("\n🔍 Exemplo de Metadados:")
        for i, doc in enumerate(docs[:3]):
            print(f"Chunk {i+1}:")
            print(f"  Tipo Documento: {doc.metadata.get('doc_type')}")
            print(f"  Origem: {doc.metadata.get('source')}")
            print(f"  Página: {doc.metadata.get('page')}\n")

    print(f"\n📄 Exibindo conteúdo do Chunk {i+1}:")
    if docs:
        print("🔍 Exemplo de Conteúdo:")
        # Mostra apenas os 3 primeiros chunks
        for i, doc in enumerate(docs[:3]):
            print(f"\n=== Chunk {i+1} ===")

            # Mostra os primeiros 500 caracteres
            print(f"Conteúdo:\n{doc.page_content[:500]}...")
            print("=" * 50)

    print(f"\n🔍 Metadados do Chunk {i+1}: 'chunks_output.txt'\n")
    # Salvar os chunks no arquivo txt
    save_chunks_to_txt(docs, file_path="chunks_output.txt")

    # Salva os chunks como arquivo JSON
    # save_chunks_as_json(docs)
    print(f"\n\n")

    print(f"📝 Metadados: {len(docs[0].metadata)} ")  # Verifique os metadados
    print(f"📚 Total de documentos processados: {len(docs)}")


if __name__ == "__main__":
    run_test()
# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_local_process_copy
