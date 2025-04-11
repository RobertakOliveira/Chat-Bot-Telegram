import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from LLM import  BedrockLLM
from classe_embedding import BedrockEmbeddings

def main():
    # Carregamento dos PDFs jurídicos
    dataset_path = "./dataset"
    loader = DirectoryLoader(dataset_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"{len(documents)} documentos carregados.")

    if not documents:
        print("Nenhum documento encontrado. Verifique o caminho do dataset!")
        return

    # Divisão dos textos em chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    print(f"{len(docs)} chunks gerados.")

    # Criação ou carregamento do índice no Chroma com os embeddings do Amazon Bedrock
    embeddings = BedrockEmbeddings()
    persist_directory = "chroma_db"

    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        print("Carregando índice já existente...")
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    else:
        print("Criando novo índice e persistindo os dados...")
        vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=persist_directory)
        vectorstore.persist()
    print("Indexação concluída.")

    # Configuração do retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Configuração do LLM com streaming ativado
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    bedrock_llm = BedrockLLM(streaming=True, callback_manager=callback_manager)

    # Criação de um prompt customizado para a tarefa jurídica
    custom_template = (
        "Você é um assistente jurídico altamente especializado. Utilize as informações contidas nos trechos "
        "dos documentos fornecidos para responder a pergunta a seguir de maneira clara, precisa e fundamentada.\n\n"
        "Documentos:\n{context}\n\n"
        "Pergunta:\n{input}\n\n"
        "Sua resposta deve:\n"
        "- Resumir os argumentos principais apresentados nos documentos.\n"
        "- Destacar os pontos relevantes relativos à inadmissibilidade do recurso.\n"
        "- Utilizar uma linguagem formal e técnica, adequada ao meio jurídico.\n"
        "- Indicar, se necessário, que não foi possível encontrar uma resposta completa, caso a informação não esteja presente.\n\n"
        "Resposta:"
    )
    custom_prompt = PromptTemplate(
        template=custom_template,
        input_variables=["context", "input"]
    )

    # Criação das chains: combine_documents e a chain de recuperação (RAG)
    combine_docs_chain = create_stuff_documents_chain(bedrock_llm, custom_prompt)
    qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

    # Exemplo de consulta
    query = "Quais os argumentos apresentados sobre inadmissibilidade do recurso nos documentos?"
    print(f"\nConsulta: {query}\n")
    resposta = qa_chain.invoke({"input": query})
    final_answer = resposta.get("answer", "")
    print("Resposta gerada:\n", final_answer)

if __name__ == "__main__":
    main()
