import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db_producao")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "producao")
    AWS_PROFILE = os.getenv("AWS_PROFILE")
    AWS_REGION = os.getenv("AWS_REGION")
    EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
    LLM_MODEL = "amazon.nova-pro-v1:0"
    