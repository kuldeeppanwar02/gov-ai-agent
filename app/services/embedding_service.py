import boto3
import json
from app.config import AWS_REGION, TITAN_EMBED_MODEL_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID if AWS_ACCESS_KEY_ID else None,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY if AWS_SECRET_ACCESS_KEY else None,
)


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
