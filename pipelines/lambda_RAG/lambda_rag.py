# main.py

import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrockConverse
from classe_embedding import BedrockEmbeddings

def main():
    # 3. Criação ou carregamento do índice Chroma com embeddings do Bedrock
    embeddings = BedrockEmbeddings()
    persist_directory = "chroma_db"
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        print("Carregando índice já existente...")
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)



    # 5. Instanciação do modelo conversacional Bedrock
    model = ChatBedrockConverse(
        model="amazon.nova-pro-v1:0",
        region_name="us-east-1"
    )

    # 6. Prompt customizado como template de conversa
    prompt = ChatPromptTemplate.from_messages([
        ("human", "Você é um assistente jurídico altamente especializado. Utilize as informações contidas nos trechos "
        "dos documentos fornecidos para responder a pergunta a seguir de maneira clara, precisa e fundamentada.\n\n"
        "Documentos:\n{context}\n\n"
        "Pergunta:\n{input}\n\n"
        "Sua resposta deve:\n"
        "- Utilizar uma linguagem formal e técnica, adequada ao meio jurídico.\n"
        "- Indicar, se necessário, que não foi possível encontrar uma resposta completa, caso a informação não esteja presente.\n\n"
        "Resposta:"
    )
    ])

    # 7. Criação da chain
    chain = prompt | model

    # 8. Consulta
    query = "Qual a tese defendida por Willy Fonseca Tempel em seu Recurso Extraordinário contra o INSS?"
    print(f"\nConsulta: {query}\n")

    # 9. Recupera os trechos relevantes
    # Recupera os documentos relevantes com scores de similaridade
    results_with_scores = vectorstore.similarity_search_with_score(query, k=3)

    # Exibe os scores e os documentos
    print("\nChunks retornados com similaridade:")
    context_parts = []
    for i, (doc, score) in enumerate(results_with_scores, 1):
        raw_source = doc.metadata.get("source", "desconhecido")
        page = doc.metadata.get("page", "n/d")
        print(f"Chunk {i}: Similaridade: {round(score, 4)} | Arquivo: {raw_source}, Página: {page}")
        context_parts.append(doc.page_content)


    # Junta os conteúdos para o prompt
    context = "\n\n".join(context_parts)


    # 10. Executa a cadeia conversacional
    resposta = chain.invoke({"input": query, "context": context})

    # 11. Exibe a resposta
    print("\nResposta gerada:\n", resposta.content)

if __name__ == "__main__":
    main()
