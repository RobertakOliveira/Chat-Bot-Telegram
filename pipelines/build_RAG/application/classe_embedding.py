import json
import boto3
from langchain.embeddings.base import Embeddings
from langchain.llms.base import LLM
from pydantic import PrivateAttr



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
