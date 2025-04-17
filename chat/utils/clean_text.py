# chat/utils/clean_text.py
import re
from chat.utils.config import bedrock_config


def clean_text(text: str) -> str:
    """Truncagem baseada em estimativa de tokens (1 token ≈ 4 caracteres)"""
    max_chars = int(bedrock_config.TEXT_TRUNCATE * 5.2 * 0.90)
    clean_text = text.replace('\x00', '').replace('\u200b', '').strip()
    return clean_text[:max_chars]
