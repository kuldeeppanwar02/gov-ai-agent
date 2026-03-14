import boto3
import json
from app.config import AWS_REGION, TITAN_EMBED_MODEL_ID

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def embed_text(text: str) -> list[float]:
    """
    Embed a text string using Amazon Titan Embed Text v2 via Bedrock.
    Returns a list of floats (embedding vector).
    """
    response = bedrock.invoke_model(
        modelId=TITAN_EMBED_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "inputText": text[:8000]   # Titan has 8k token limit
        })
    )
    body = json.loads(response["body"].read())
    return body["embedding"]
