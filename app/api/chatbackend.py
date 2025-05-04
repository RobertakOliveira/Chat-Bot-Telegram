import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from langchain_aws import BedrockLLM
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_aws.embeddings import BedrockEmbeddings

# Inicialização do FastAPI
app = FastAPI(
    title="Chatbot Jurídico API",
    description="API para o chatbot jurídico baseado em AWS Bedrock",
    version="1.0.0"
)

# Modelos Pydantic para validação de dados
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Dicionário para armazenar memórias de sessão
session_memories: Dict[str, ConversationBufferWindowMemory] = {}

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

def get_chat_response(input_text: str, memory: ConversationBufferWindowMemory) -> str:
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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Se não houver session_id, criar uma nova sessão
        if not request.session_id:
            request.session_id = os.urandom(16).hex()
            session_memories[request.session_id] = create_memory()
        
        # Verificar se a sessão existe
        if request.session_id not in session_memories:
            session_memories[request.session_id] = create_memory()
        
        # Obter memória da sessão
        memory = session_memories[request.session_id]
        
        # Obter resposta do chatbot
        response = get_chat_response(request.message, memory)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Teste local (mantido para desenvolvimento)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)