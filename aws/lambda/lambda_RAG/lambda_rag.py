import os
import json
import boto3
import time
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings

#######################################
# 1. Wrapper customizado para embeddings usando o modelo amazon.titan-embed-text-v2:0
#######################################

class BedrockEmbeddings(Embeddings):
    """
    Implementa a interface de embeddings do LangChain utilizando o Amazon Bedrock.
    Aqui usamos o modelo de embeddings 'amazon.titan-embed-text-v2:0' para processar os textos
    dos documentos jurídicos.
    """
    def __init__(self, model_id: str = "amazon.titan-embed-text-v2:0", region: str = "us-east-1"):
        self.model_id = model_id
        self.region = region
        # Cria o cliente para chamada ao serviço Bedrock
        self.client = boto3.client('bedrock-runtime', region_name=self.region)

    def _get_embedding(self, text: str) -> list[float]:
        # Prepara o payload; aqui pode ser necessário adaptar o formato do payload conforme a documentação atual do serviço
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
        # Extraia o embedding da resposta. Ajuste a extração conforme o retorno real do serviço.
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
    """
    Implementa um LLM que utiliza o Amazon Bedrock para a geração de respostas.
    (Caso você tenha um modelo específico para geração de texto, pode ajustar aqui.
     Muitas vezes, na mesma conta da AWS, o serviço pode oferecer modelos de chat ou de completions.)
    """
    def __init__(self, model_id: str, region: str = "us-east-1"):
        self.model_id = model_id
        self.region = region
        self.client = boto3.client("bedrock-runtime", region_name=self.region)

    @property
    def _llm_type(self) -> str:
        return "bedrock"

    def _call(self, prompt: str, stop: list[str] = None) -> str:
        payload = {"prompt": prompt}
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(payload),
            contentType="application/json"
        )

        result_str = response["Body"].read().decode("utf-8")
        result = json.loads(result_str)
        # Ajuste conforme o formato de saída do modelo Bedrock para geração de texto
        generated_text = result.get("generated_text", "")
        return generated_text

#######################################
# 3. Pipeline RAG adaptado para documentos jurídicos
#######################################

def main():
    # --- Carregamento dos PDFs jurídicos usando DirectoryLoader e PyPDFLoader.
    # Assumimos que a estrutura de pastas (com subpastas) esteja dentro da pasta './dataset'
    dataset_path = "./dataset"
    loader = DirectoryLoader(dataset_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"{len(documents)} documentos carregados.")

    if not documents:
        print("Nenhum documento encontrado. Verifique o caminho do dataset!")
        return

    # --- (Opcional) Pré-processamento: para documentos jurídicos pode ser interessante
    # remover quebras de linhas excessivas ou normalizar caracteres. Aqui você pode aplicar funções adicionais.

    # --- Divisão dos textos em chunks
    # O tamanho dos chunks e a sobreposição podem ser ajustados para garantir que partes importantes do texto não sejam truncadas.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    # O método split_documents preserva os metadados (como nome do arquivo e caminho)
    docs = text_splitter.split_documents(documents)
    print(f"{len(docs)} chunks gerados.")

    # --- Criação do índice no Chroma utilizando os embeddings do Amazon Bedrock (modelo amazon.titan-embed-text-v2:0)
    embeddings = BedrockEmbeddings()  # O modelo já vem definido como 'amazon.titan-embed-text-v2:0'
    # persist_directory permite salvar o índice para futuras consultas sem precisar reprocessar tudo
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="chroma_db")
    print("Indexação concluída.")

    # --- Configuração do retriever para buscar os chunks mais relevantes
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # --- Configuração do LLM para geração da resposta final via Bedrock.
    # Substitua o model_id abaixo com o modelo adequado para geração (se diferente do de embeddings).
    bedrock_llm = BedrockLLM(model_id="seu-modelo-bedrock-llm", region="us-east-1")

    # --- Criação da cadeia de Recuperação (RAG) com LangChain
    qa_chain = RetrievalQA(llm=bedrock_llm, retriever=retriever)
    
    # --- Exemplo de consulta: como os documentos são jurídicos, a pergunta pode ser,
    # por exemplo, “Quais os argumentos apresentados sobre inadmissibilidade do recurso?”
    query = "Quais os argumentos apresentados sobre inadmissibilidade do recurso nos documentos?"
    print(f"\nConsulta: {query}\n")
    
    # Executa a cadeia para obter a resposta final
    resposta = qa_chain.run(query)
    print("Resposta gerada:\n", resposta)

if __name__ == "__main__":
    main()
