import json
from app.config import TITAN_EMBED_MODEL_ID, bedrock_invoke


def embed_text(text: str) -> list[float]:
    """
    Embed a text string using Amazon Titan Embed Text v2 via Bedrock.
    Returns a list of floats (embedding vector).
    Uses bedrock_invoke() to bypass botocore double URL-encoding bug.
    """
    result = bedrock_invoke(TITAN_EMBED_MODEL_ID, {
        "inputText": text[:8000]   # Titan has 8k token limit
    })
    return result["embedding"]
