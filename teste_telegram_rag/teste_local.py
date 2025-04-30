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
        ("human", "Você é um assistente jurídico de alta competência técnica e rigor analítico. "
        "Sua tarefa é utilizar exclusivamente as informações contidas nos trechos dos documentos fornecidos para elaborar uma resposta à pergunta apresentada.\n\n"
        "Diretrizes obrigatórias:\n"
        "- Utilize linguagem formal, precisa e estritamente técnica, conforme o padrão jurídico.\n"
        "- Fundamente suas respostas com base nos documentos, citando os trechos relevantes de maneira integrada ao texto.\n"
        "- Se a informação necessária não estiver presente ou for insuficiente, declare expressamente a limitação, sem tentar supor ou inferir dados ausentes.\n"
        "- Estruture a resposta de forma clara, coesa e organizada, utilizando parágrafos bem desenvolvidos.\n\n"
        "Formato da tarefa:\n"
        "- Introdução breve contextualizando o tema da pergunta (se aplicável).\n"
        "- Análise fundamentada com base nos documentos fornecidos.\n"
        "- Conclusão objetiva, explicitando o alcance ou a limitação da resposta conforme a documentação disponível.\n\n"
        "Exemplos Modelares (não relacionados aos casos de teste):\n"
        "- Elaboração de parecer sobre a validade de uma cláusula contratual com base em trechos do Código Civil.\n"
        "- Análise de um pedido de indenização a partir de excertos da legislação trabalhista.\n"
        "- Resposta a uma consulta sobre regime de bens no casamento com base em jurisprudência selecionada.\n\n"
        "Dados fornecidos:\n"
        "Documentos:\n{context}\n\n"
        "Pergunta:\n{input}\n\n"
        "Inicie sua resposta abaixo:\n"
        "Resposta:")
    ])

    # 5. Montagem da chain
    chain = prompt | model

    # 6. Exemplo de consulta
    query = "batata?"
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
