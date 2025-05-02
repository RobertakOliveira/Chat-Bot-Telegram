from Rag.aws.aws_session import initialize_models
from Rag.chroma_conector import connect_chroma
from Rag.prompt_template import create_prompt_template
from langchain.chains import RetrievalQAWithSourcesChain

class JusBotRAG:
    def __init__(self):
        self.embeddings, self.llm = initialize_models()
        self.chroma_db = connect_chroma(self.embeddings)
        self.qa_prompt = create_prompt_template()

    def query_document(self, question, document_name=None):
        retriever = self.chroma_db.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5 if document_name else 20,
                "filter": {"source": document_name} if document_name else None
            }
        )

        qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": self.qa_prompt, "document_variable_name": "context"},
            return_source_documents=True,
            verbose=True
        )

        result = qa_chain.invoke({"question": question})
        return result.get("answer", "❌ Nenhuma resposta gerada.")

    def listar_documentos(self):
        collection = self.chroma_db._collection
        metadatas = collection.get(include=["metadatas"])["metadatas"]
        return sorted({m["source"] for m in metadatas if "source" in m})

if __name__ == "__main__":
    rag_system = JusBotRAG()
    rag_system.listar_documentos()
    #Modo de uso
    pergunta = "Retorne os documentos com IOLANDA SANTOS GUIMARÃES"
    resposta = rag_system.query_document(pergunta)

    print("\nResposta do JusBot:")
    print(resposta)
