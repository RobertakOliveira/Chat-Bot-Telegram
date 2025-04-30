import boto3
import os
from typing import Optional
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_aws.chat_models import ChatBedrock
from langchain_chroma import Chroma
from chromadb import PersistentClient
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Configurações
class Config:
    CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db_producao")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "producao")
    AWS_PROFILE = os.getenv("AWS_PROFILE")
    AWS_REGION = os.getenv("AWS_REGION")
    EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
    LLM_MODEL = "amazon.nova-pro-v1:0"

# Sessão AWS
boto3.setup_default_session(profile_name=Config.AWS_PROFILE)
boto3_bedrock = boto3.client("bedrock-runtime", region_name=Config.AWS_REGION)

# Inicializar embeddings e LLM
def initialize_models():
    try:
        embeddings = BedrockEmbeddings(
            model_id=Config.EMBEDDING_MODEL,
            client=boto3_bedrock
        )
        llm = ChatBedrock(
            model_id=Config.LLM_MODEL,
            client=boto3_bedrock,
            model_kwargs={
                "max_tokens": 1000,
                "temperature": 0,
                "top_p": 0.9
            }
        )
        return embeddings, llm
    except Exception as e:
        print(f"❌ Erro ao inicializar modelos AWS Bedrock: {e}")
        raise

# Conectar ao ChromaDB
def connect_chroma(embeddings):
    client = PersistentClient(path=Config.CHROMA_DIR)
    chroma = Chroma(
        collection_name=Config.COLLECTION_NAME,
        embedding_function=embeddings,
        client=client
    )
    return chroma

# Template de prompt
def create_prompt_template():
    system_message = """Você é o JusBot, um assistente jurídico altamente especializado na análise de documentos legais. 

Metodologia de análise (obrigatória):
1. Identifique os conceitos jurídicos principais da consulta
2. Localize as informações específicas no contexto fornecido
3. Verifique a correspondência exata entre pergunta e documento
4. Estruture uma resposta técnica baseada exclusivamente no documento

Diretrizes obrigatórias:
- Responda exclusivamente com base no contexto fornecido
- Se a informação não estiver explícita no contexto, diga: "Não encontrei esta informação no documento."
- Reproduza fielmente números de processo, trechos citados e nomes próprios conforme aparecem no documento
- Use formatação em tópicos ou itens numerados quando a resposta envolver múltiplos elementos
- Seja direto, técnico e objetivo. Evite introduções, rodeios ou opiniões pessoais
- Caso a pergunta solicite uma lista, enumere os itens claramente

Exemplo 1:
Pergunta: Quais são os prazos para interposição de recurso especial mencionados no documento?
Contexto: [Trecho de documento jurídico]
O recurso especial, previsto no art. 105, III da Constituição Federal, deverá ser interposto no prazo de 15 (quinze) dias, conforme disposto no art. 1.003, §5º do Código de Processo Civil. Para casos anteriores à vigência do CPC/2015, aplicava-se o prazo de 15 dias previsto na Lei 8.038/90.

Pensamento: A pergunta solicita informações sobre prazos para interposição de recurso especial. Analisando o documento, encontro menção explícita a um prazo de 15 dias conforme o art. 1.003, §5º do CPC, além de referência ao mesmo prazo para casos anteriores à vigência do CPC/2015. Vou estruturar a resposta em tópicos com as informações exatas do documento.

Resposta:
Os prazos para interposição de recurso especial mencionados no documento são:
1. 15 (quinze) dias, conforme art. 1.003, §5º do Código de Processo Civil (para casos regidos pelo CPC/2015)
2. 15 dias previstos na Lei 8.038/90 (para casos anteriores à vigência do CPC/2015)

Exemplo 2:
Pergunta: Quais são os requisitos para concessão de tutela de urgência segundo o documento?
Contexto: [Trecho de documento jurídico]
O juiz poderá analisar medidas conservativas para evitar dano de difícil reparação. O documento não especifica requisitos para tutela de urgência.

Pensamento: A pergunta solicita os requisitos para concessão de tutela de urgência. Ao analisar o contexto fornecido, verifico que o documento menciona medidas conservativas para evitar dano, mas não especifica explicitamente os requisitos para tutela de urgência. Conforme as diretrizes, devo informar quando uma informação não está presente no documento.

Resposta: Não encontrei esta informação no documento.
"""
    human_message = """
Pergunta: {question}
Contexto: {context}

Gere uma resposta precisa e fundamentada, utilizando exclusivamente as informações do contexto acima.
"""
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(human_message)
    ])

# Pipeline RAG
class JusBotRAG:
    def __init__(self):
        self.embeddings, self.llm = initialize_models()
        self.chroma_db = connect_chroma(self.embeddings)
        self.qa_prompt = create_prompt_template()

        self.retriever = self.chroma_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )

    def query_document(self, question: str, document_name: Optional[str] = None):
        try:
            # Decide qual retriever usar
            if document_name:
                print(f"🔎 Filtro por documento específico: {document_name}")
                retriever = self.chroma_db.as_retriever(
                    search_type="similarity",
                    search_kwargs={
                        "k": 5,
                        "filter": {"source": document_name}
                    }
                )
            else:
                print("🔍 Busca geral na base de documentos...")
                retriever = self.chroma_db.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 20}
                )

            # Cria diretamente o RetrievalQA Chain
            qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
                llm=self.llm,
                retriever=retriever,
                chain_type="stuff",
                chain_type_kwargs={
                    "prompt": self.qa_prompt,
                    "document_variable_name": "context"
                },
                return_source_documents=True,
                verbose=True
            )

            result = qa_chain.invoke({"question": question})
            resposta = result.get("answer", "").strip()

            if not resposta:
                print("⚠️ LLM não conseguiu gerar resposta.")
                return "❌ Não encontrei resposta adequada."

            # Mostrar fontes dos documentos usados
            if "source_documents" in result:
                print("\n--- Fontes utilizadas ---")
                for idx, doc in enumerate(result["source_documents"]):
                    print(f"[{idx}] Fonte: {doc.metadata.get('source', 'desconhecido')}")
                print("--- Fim das fontes ---\n")

            print("✅ Resposta gerada com sucesso!")
            return resposta

        except Exception as e:
            print(f"❌ Erro na consulta: {str(e)}")
            return "❌ Ocorreu um erro ao processar sua consulta."

    def listar_documentos(self):
        collection = self.chroma_db._collection
        all_metadatas = collection.get(include=["metadatas"])["metadatas"]

        sources = set()
        for metadata in all_metadatas:
            if metadata and "source" in metadata:
                sources.add(metadata["source"])

        documentos_ordenados = sorted(list(sources))

        print("\n📚 Documentos disponíveis no Chroma:")
        for src in documentos_ordenados:
            print(f" - {src}")

        return documentos_ordenados

# Exemplo de uso
if __name__ == "__main__":
    rag_system = JusBotRAG()
    rag_system.listar_documentos()
    #Modo de uso
    pergunta = "Retorne os documentos com IOLANDA SANTOS GUIMARÃES"
    resposta = rag_system.query_document(pergunta)

    print("\nResposta do JusBot:")
    print(resposta)
