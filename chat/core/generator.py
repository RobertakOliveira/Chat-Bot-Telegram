# chat/core/generator.py
import boto3
import json
from chat.utils.logger import get_logger
from chat.utils.prompt_template import prompt_template  # Importe o template
from botocore.exceptions import BotoCoreError, ClientError

logger = get_logger("Geração de Respostas Jurídicas com Base nos Documentos")

BEDROCK_MODEL_ID = "amazon.nova-pro-v1:0"
REGION = "us-east-1"

# Inicializa o cliente para acessar o serviço Bedrock Runtime
bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)

def generate_response(context: str, question: str) -> str:
    """
    Gera uma resposta com base no contexto e pergunta usando o Amazon Nova Pro.
    Utiliza um template para gerar o prompt para o modelo.

    Args:
        context (str): O contexto relevante para responder a pergunta.
        question (str): A pergunta feita pelo usuário.
        
    Returns:
        str: A resposta gerada pelo modelo ou mensagem de erro.
    """
    try:
        logger.info("🔁 Chamando Amazon Nova Pro com prompt gerado...")

        # Cria o prompt formatado a partir do contexto e pergunta, baseado no template do assistente jurídico
        prompt = prompt_template(context, question)

        # Prepara o payload no formato esperado pelo modelo, com o prompt incluído como mensagem de usuário
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        # Envia o payload para o modelo usando o método invoke_model da API Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )

        # Lê e decodifica o corpo da resposta do modelo
        # Espera-se que a resposta venha no formato:
        # { "output": { "message": { "content": [ { "text": <texto gerado> }, ... ] } } }
        response_body = json.loads(response["body"].read())
        completion = "Sem resposta."  # Valor padrão, caso nada seja retornado

        # Verifica se há uma mensagem válida na resposta
        if "output" in response_body and "message" in response_body["output"]:
            content_list = response_body["output"]["message"].get("content", [])
            if content_list and isinstance(content_list, list):
                # Extrai o primeiro texto gerado pelo modelo
                completion = content_list[0].get("text", completion)
            else:
                logger.warning("⚠️ Resposta recebida, mas sem conteúdo útil para extrair.")
                
        logger.info("✅ Resposta gerada com sucesso.")
        return completion

    # Captura e loga erros específicos da AWS (ex: problemas de permissão, rede, etc.)
    except (BotoCoreError, ClientError) as aws_err:
        logger.error(f"📡 Erro da AWS: {json.dumps(aws_err.response, indent=4)}")
        return "Erro ao se comunicar com o modelo na AWS."

    # Captura e loga qualquer outro erro inesperado
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return "Erro interno inesperado."