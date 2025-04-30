# main.py

import os
import boto3
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrockConverse
from classe_embedding import BedrockEmbeddings

def sync_s3_folder(bucket_name: str, prefix: str, local_dir: str):
    """
    Faz download recursivo de todos os objetos em bucket_name/prefix
    para a pasta local local_dir, preservando a estrutura.
    """
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            # pula “pastas” vazias
            if key.endswith("/"):
                continue
            # caminho relativo dentro de chroma_db/
            rel_path = key[len(prefix):]
            local_path = os.path.join(local_dir, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(bucket_name, key, local_path)
    print(f"✅ Sincronizado s3://{bucket_name}/{prefix} → {local_dir}/")

def main():
    # 1. Sincroniza o chroma_db do S3 (apenas se ainda não existir localmente)
    bucket_name = "bucketembeddingssprint7"
    prefix = "chroma_db/"
    persist_directory = "chroma_db"

    if not (os.path.exists(persist_directory) and os.listdir(persist_directory)):
        os.makedirs(persist_directory, exist_ok=True)
        sync_s3_folder(bucket_name, prefix, persist_directory)
    else:
        print("📂 chroma_db já existe localmente, pulando download.")

    # 2. Criação ou carregamento do índice Chroma com embeddings do Bedrock
    embeddings = BedrockEmbeddings()
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    # 3. Instanciação do modelo conversacional Bedrock
    model = ChatBedrockConverse(
        model="amazon.nova-pro-v1:0",
        region_name="us-east-1"
    )

    # 4. Prompt customizado
    prompt = ChatPromptTemplate.from_messages([
        ("human", 
         "Você é um assistente jurídico altamente especializado. Utilize as informações contidas nos trechos "
         "dos documentos fornecidos para responder a pergunta a seguir de maneira clara, precisa e fundamentada.\n\n"
         "Documentos:\n{context}\n\n"
         "Pergunta:\n{input}\n\n"
         "Sua resposta deve:\n"
         "- Utilizar uma linguagem formal e técnica, adequada ao meio jurídico.\n"
         "- Indicar, se necessário, que não foi possível encontrar uma resposta completa, caso a informação não esteja presente.\n\n"
         "Resposta:")
    ])

    # 5. Montagem da chain
    chain = prompt | model

    # 6. Exemplo de consulta
    query = "Qual a tese defendida por Willy Fonseca Tempel em seu Recurso Extraordinário contra o INSS?"
    print(f"\nConsulta: {query}\n")

    # 7. Recupera os 3 chunks mais similares
    results_with_scores = vectorstore.similarity_search_with_score(query, k=3)
    print("\nChunks retornados com similaridade:")
    context_parts = []
    for i, (doc, score) in enumerate(results_with_scores, 1):
        src = doc.metadata.get("source", "desconhecido")
        pg  = doc.metadata.get("page", "n/d")
        print(f"Chunk {i}: score={score:.4f} | {src} (pág. {pg})\n")
        print(doc.page_content, "\n" + "-"*50 + "\n")
        context_parts.append(doc.page_content)

    # 8. Executa a chain
    context = "\n\n".join(context_parts)
    resposta = chain.invoke({"input": query, "context": context})

    # 9. Exibe a resposta
    print("\nResposta gerada:\n", resposta.content)

if __name__ == "__main__":
    main()
