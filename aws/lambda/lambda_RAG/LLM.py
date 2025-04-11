import json
import boto3
from langchain.embeddings.base import Embeddings
from langchain.llms.base import LLM
from pydantic import PrivateAttr



class BedrockLLM(LLM):
    """
    Wrapper customizado para o Amazon Bedrock, com suporte a streaming dos tokens.
    """
    model_id: str = "amazon.titan-text-premier-v1:0"
    region: str = "us-east-1"
    streaming: bool = False
    _client: any = PrivateAttr()

    @property
    def _llm_type(self) -> str:
        return "bedrock"

    def __init__(self, streaming: bool = False, **data):
        super().__init__(**data)
        self.streaming = streaming
        self._client = boto3.client("bedrock-runtime", region_name=self.region)

    def _call(self, prompt: str, stop: list[str] = None) -> str:
        """
        Se o streaming estiver habilitado, agrega os tokens conforme são emitidos.
        """
        if self.streaming:
            full_text = ""
            for token in self._stream(prompt, stop):
                full_text += token
            return full_text

        payload = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 3072,
                "stopSequences": stop or [],
                "temperature": 0.1,
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
        generated_text = ""
        if "results" in result and len(result["results"]) > 0:
            generated_text = result["results"][0].get("outputText", "")
        return generated_text

    def _stream(self, prompt: str, stop: list[str] = None):
        """
        Simula o streaming dividindo a resposta em tokens e enviando-os via callback_manager (se configurado).
        """
        payload = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 3072,
                "stopSequences": stop or [],
                "temperature": 0.1,
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
        full_text = ""
        if "results" in result and len(result["results"]) > 0:
            full_text = result["results"][0].get("outputText", "")
        tokens = full_text.split()
        for token in tokens:
            token_with_space = token + " "
            if self.callback_manager:
                self.callback_manager.on_llm_new_token(token_with_space)
            yield token_with_space
