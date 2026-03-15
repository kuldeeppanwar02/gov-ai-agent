import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def _clean_var(name: str, default: str = "") -> str:
    """Robustly clean environment variables: strip quotes, spaces, and hidden line endings."""
    val = os.getenv(name, default)
    if not val:
        return ""
    # Remove quotes, newlines, tabs, and spaces
    return val.strip().strip('"').strip("'").replace("\r", "").replace("\n", "").replace("\t", "").strip()

# AWS Settings
AWS_REGION = _clean_var("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = _clean_var("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = _clean_var("AWS_SECRET_ACCESS_KEY")

# S3
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "gov-ai-agent-bucket")

# Amazon Bedrock Model IDs
NOVA_LITE_MODEL_ID = "amazon.nova-lite-v1:0"
TITAN_EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"

# Nova Act
NOVA_ACT_API_KEY = os.getenv("NOVA_ACT_API_KEY", "")

# OpenSearch (optional)
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "")
OPENSEARCH_REGION = os.getenv("OPENSEARCH_REGION", "us-east-1")

# App
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Centralized Bedrock Client
def get_bedrock_client():
    """Returns a centralized bedrock-runtime client with explicit credentials."""
    print(f"🔧 Initializing Bedrock client in region: {AWS_REGION}")
    
    # Logic to handle empty env vars (os.getenv returns empty string, not None)
    key_id = AWS_ACCESS_KEY_ID if AWS_ACCESS_KEY_ID else None
    secret = AWS_SECRET_ACCESS_KEY if AWS_SECRET_ACCESS_KEY else None
    
    # Diagnostic logging (Safe/Masked)
    if key_id:
        masked_id = f"{key_id[:4]}...{key_id[-4:]}"
        print(f"🔑 AWS_ACCESS_KEY_ID: {masked_id} (Length: {len(key_id)})")
    else:
        print("⚠️ AWS_ACCESS_KEY_ID is NOT_SET or EMPTY")

    if secret:
        print(f"🔐 AWS_SECRET_ACCESS_KEY: (Length: {len(secret)})")
        if len(secret) != 40:
            print(f"🚨 WARNING: AWS Secret Key length is {len(secret)}, expected 40. Please check for extra/missing characters.")
    else:
        print("⚠️ AWS_SECRET_ACCESS_KEY is NOT_SET or EMPTY")
    
    return boto3.client(
        "bedrock-runtime",
        region_name=AWS_REGION,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
    )

# Singleton instance
bedrock_client = get_bedrock_client()

