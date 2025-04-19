import os
from langchain_aws import BedrockLLM
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_aws.embeddings import BedrockEmbeddings

# Configuração dos embeddings
embeddings = BedrockEmbeddings(
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    model_id="amazon.titan-embed-text-v2:0"
)

chroma_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

def amazon_llm():
    return BedrockLLM(
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        model_id="amazon.titan-text-express-v1",
        model_kwargs={
            "temperature": 0.3,
            "maxTokenCount": 1024,
            "topP": 0.9
        }
    )

def create_memory():
    return ConversationBufferWindowMemory(
        k=3,
        memory_key="chat_history",
        return_messages=True
    )

def get_chat_response(input_text, memory):
    llm = amazon_llm()
    
    prompt_template = """Você é um assistente jurídico. Responda com base no contexto:

Contexto:
{context}

Pergunta: {question}

Formato da resposta:
1. Base legal (artigos)
2. Explicação resumida
Resposta:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=chroma_db.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    
    result = qa_chain({"query": input_text})
    return result["result"]

# Teste
if __name__ == "__main__":
    memory = create_memory()
    print("Chatbot Jurídico (Digite 'sair' para encerrar)")
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() == "sair":
            break
        
        response = get_chat_response(user_input, memory)
        print("\nAssistente:", response)