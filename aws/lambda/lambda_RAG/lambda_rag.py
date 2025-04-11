import os
import json
import boto3
import time
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.llms.base import LLM
from pydantic import PrivateAttr
from langchain.embeddings.base import Embeddings

# Importação para criação da chain de combinação de documentos
from langchain.chains.combine_documents import create_stuff_documents_chain
# Importa o PromptTemplate para definir o prompt customizado
from langchain.prompts import PromptTemplate

#######################################
# 1. Wrapper customizado para embeddings usando o modelo amazon.titan-embed-text-v2:0
#######################################

class BedrockEmbeddings(Embeddings):
    """
    Implementa a interface de embeddings do LangChain utilizando o Amazon Bedrock.
    Utiliza o modelo 'amazon.titan-embed-text-v2:0' para processar textos dos documentos jurídicos.
    """
    def __init__(self, model_id: str = "amazon.titan-embed-text-v2:0", region: str = "us-east-1"):
        self.model_id = model_id
        self.region = region
        self.client = boto3.client('bedrock-runtime', region_name=self.region)

    def _get_embedding(self, text: str) -> list[float]:
        payload = {
            "inputText": text,
            "dimensions": 512,
            "normalize": True
        }
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(payload),
            contentType="application/json"
        )
        result_str = response["body"].read().decode("utf-8")
        result = json.loads(result_str)
        embedding = result.get("embedding", [])
        return embedding

    def embed_query(self, text: str) -> list[float]:
        return self._get_embedding(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._get_embedding(t) for t in texts]

#######################################
# 2. Wrapper customizado para o LLM usando o Amazon Bedrock
#######################################

class BedrockLLM(LLM):
    # Declaração dos campos para o Pydantic
    model_id: str = "amazon.titan-text-premier-v1:0"
    region: str = "us-east-1"
    _client: any = PrivateAttr()

    @property
    def _llm_type(self) -> str:
        return "bedrock"

    def __init__(self, **data):
        super().__init__(**data)
        self._client = boto3.client("bedrock-runtime", region_name=self.region)

    def _call(self, prompt: str, stop: list[str] = None) -> str:
        payload = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 3072,
                "stopSequences": stop or [],
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        response = self._client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )
        result_str = response["body"].read().decode("utf-8")
        result = json.loads(result_str)
        # Debug: imprime a resposta completa para ver sua estrutura
        #print("DEBUG - Resposta completa:", result)
        generated_text = ""
        # Se o campo 'results' existir e não estiver vazio, extrai o outputText do primeiro resultado.
        if "results" in result and len(result["results"]) > 0:
            generated_text = result["results"][0].get("outputText", "")
        return generated_text


#######################################
# 3. Pipeline RAG adaptado para documentos jurídicos
#######################################

def main():
    # --- Carregamento dos PDFs jurídicos usando DirectoryLoader e PyPDFLoader.
    dataset_path = "./dataset"
    loader = DirectoryLoader(dataset_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"{len(documents)} documentos carregados.")

    if not documents:
        print("Nenhum documento encontrado. Verifique o caminho do dataset!")
        return

    # --- Divisão dos textos em chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    print(f"{len(docs)} chunks gerados.")

    # --- Criação do índice no Chroma utilizando os embeddings do Amazon Bedrock
    embeddings = BedrockEmbeddings()
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="chroma_db")
    print("Indexação concluída.")

    # --- Configuração do retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # --- Configuração do LLM para geração da resposta final via Bedrock.
    bedrock_llm = BedrockLLM()

    # --- Criação de um prompt customizado para a tarefa jurídica
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
    # Cria o objeto PromptTemplate especificando os placeholders esperados
    custom_prompt = PromptTemplate(
        template=custom_template,
        input_variables=["context", "input"]
    )

    # --- Criação da chain de combinação de documentos utilizando o prompt customizado
    combine_docs_chain = create_stuff_documents_chain(bedrock_llm, custom_prompt)

    # --- Criação da chain de Recuperação (RAG) utilizando o retriever e a chain de combinação
    qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

    # --- Exemplo de consulta
    query = "Quais os argumentos apresentados sobre inadmissibilidade do recurso nos documentos?"
    print(f"\nConsulta: {query}\n")
    
    # Invoca a chain RAG com a consulta; o input é passado via dicionário com a chave "input"
    resposta = qa_chain.invoke({"input": query})
    # Extraia somente a resposta final
    final_answer = resposta.get("answer", "")
    print("Resposta gerada:\n", final_answer)

if __name__ == "__main__":
    main()