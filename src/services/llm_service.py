import logging
import time
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

logger = logging.getLogger("llm_service")

class LLMService:
    def __init__(self, bedrock_client, model_id="amazon.nova-micro-v1:0", callbacks=None):
        """
        Inicializa o serviço LLM
        
        Args:
            bedrock_client: Cliente boto3 para Bedrock
            model_id: ID do modelo LLM
            callbacks: Callbacks para o modelo
        """
        logger.info(f"Inicializando LLMService com modelo {model_id}")
        self.model_id = model_id
        
        logger.debug(f"Configurando parâmetros do modelo: temperatura=0.3, maxTokenCount=512")
        self.llm = ChatBedrock(
            client=bedrock_client,
            model_id=model_id,
            model_kwargs={
                "temperature": 0.3,
                "maxTokenCount": 512,
                "stopSequences": [],
                "topP": 0.9
            },
            callbacks=callbacks or []
        )
        logger.info(f"✅ LLMService inicializado com sucesso: {model_id}")
    
    def format_chat_history(self, messages):
        """
        Formata o histórico de chat para o formato da LangChain
        
        Args:
            messages: Lista de mensagens no formato {role, content}
            
        Returns:
            list: Lista de mensagens formatadas
        """
        logger.debug(f"Formatando histórico de chat com {len(messages)} mensagens")
        formatted_messages = []
        
        for message in messages:
            content = message.get('content', '')
            role = message.get('role', '').lower()
            
            if role == 'system':
                formatted_messages.append(SystemMessage(content=content))
            elif role == 'user':
                formatted_messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                formatted_messages.append(AIMessage(content=content))
            else:
                logger.warning(f"Tipo de mensagem desconhecido: {role}, ignorando")
        
        logger.debug(f"Histórico formatado com {len(formatted_messages)} mensagens")
        return formatted_messages
    
    def create_rag_prompt(self, context, query):
        """
        Cria o prompt RAG com o contexto e a query
        
        Args:
            context: Contexto para a consulta
            query: Texto da query
            
        Returns:
            list: Lista de mensagens do prompt
        """
        logger.info(f"Criando prompt RAG para query: {query[:50]}...")
        context_length = len(context.split())
        logger.debug(f"Tamanho do contexto: {context_length} palavras")
        
        system_prompt = SystemMessage(content=(
            "Você é um assistente especializado em análise de documentos jurídicos. "
            "Sua tarefa é analisar o contexto fornecido e responder às perguntas do usuário "
            "baseando-se APENAS nas informações contidas no contexto. "
            "Se a informação não estiver no contexto, diga claramente que não encontrou essa informação. "
            "Seja direto e objetivo em suas respostas."
            "Use uma linguagem simples, para que alguem que não seja especialista consiga entender a resposta."
        ))
        
        human_prompt = HumanMessage(content=(
            f"Com base no seguinte contexto:\n\n"
            f"{context}\n\n"
            f"Por favor, responda: {query}"
        ))
        
        logger.debug("Prompt RAG criado com sucesso")
        return [system_prompt, human_prompt]
    
    def generate_response(self, messages):
        """
        Gera uma resposta usando o LLM
        
        Args:
            messages: Lista de mensagens para o modelo
            
        Returns:
            str: Resposta do modelo
        """
        logger.info(f"Iniciando geração de resposta com LLM ({self.model_id})...")
        
        # Log das mensagens de entrada (resumido)
        for idx, msg in enumerate(messages):
            content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            logger.debug(f"Mensagem {idx+1}/{len(messages)} ({type(msg).__name__}): {content_preview}")
        
        llm_start = time.time()
        try:
            response = self.llm.invoke(messages)
            llm_time = time.time() - llm_start
            logger.info(f"✅ Resposta gerada com sucesso em {llm_time:.4f}s")
            
            # Log da resposta (resumido)
            response_preview = response.content[:100] + "..." if len(response.content) > 100 else response.content
            logger.debug(f"Resposta: {response_preview}")
            
            return response.content
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta: {str(e)}")
            raise 