from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import json
import logging

logger = logging.getLogger('geqs')

class GenerateEmbeddingQueryService:
    def __init__(self, llm):
        self.llm = llm

    def generate_query(self, chat_history, query):
        """
        Generates a new query for a similarity search, based on a chat history and on a query.
        
        Args:
            chat_history: list of SystemMessage, HumanMessage, AIMessage.
            query: str

        Returns:
            {
                "worth_searching": True | False
                "refined_query": str    
            }
        """

        prompt = SystemMessage("""
        Você é um assistente que monta queries para um serviço de busca por similaridade num banco de dados de vetor.
        Com base num histórico de conversa e numa query fornecida, sua responsabilidade é responder se vale a pena buscar no BD para encontrar uma resposta e, além disso, atualizar a query providenciada para obter resultados melhroes.
        Responda SOMENTE com um JSON seguindo a estrutura:
        {{
            "worth_searching": true | false
            "refined_query": string                      
        }}
        Tal que:
        - "worth_searching": booleano. Indica se, de fato, é necessário realizar uma busca para encontrar uma resposta. Na dúvida, coloque true se a query for um pedido (subentendido ou não) ou pergunta.
        - "refined_query": string. É uma query usada no BD vetorial para buscar uma resposta para o usuário. Deve ter um valor, obrigatoriamente, se "worth_searching" for true.  
        """)

        # Formatting Chat History
        str_chat_history = ""

        for register in chat_history:
            role = "human"
            if isinstance(register, AIMessage):
                role = "ai"
            elif isinstance(register, SystemMessage):
                role = "system"

            str_chat_history += f'{role}: {register.content}\n'

        question = HumanMessage(f"""
            # Histórico de Conversa
            {str_chat_history}

            # Query
            {query}

            json:
        """)


        try: 
            res = json.loads(self.llm.invoke([prompt, question]).content)
            return res
        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return {
                "worth_searching": False,
                "refined_query": "",
                "error": True 
            }