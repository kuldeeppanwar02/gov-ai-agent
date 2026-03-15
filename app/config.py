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
    """Returns a centralized bedrock-runtime client with explicit or IAM credentials."""
    print(f"🔧 Initializing Bedrock client in region: {AWS_REGION}")
    
    # Logic to handle empty env vars (supports IAM Roles if keys are missing)
    key_id = AWS_ACCESS_KEY_ID if AWS_ACCESS_KEY_ID else None
    secret = AWS_SECRET_ACCESS_KEY if AWS_SECRET_ACCESS_KEY else None
    
    # Setup kwargs for boto3
    client_kwargs = {
        "region_name": AWS_REGION
    }
    
    # Only add credentials if they were explicitly provided (e.g. for Render)
    # If None, boto3 will automatically use IAM Instance Roles (for App Runner)
    if key_id and secret:
        client_kwargs["aws_access_key_id"] = key_id
        client_kwargs["aws_secret_access_key"] = secret
        masked_id = f"{key_id[:4]}...{key_id[-4:]}"
        print(f"🔑 Using explicit credentials: {masked_id} (Length: {len(key_id)})")
    else:
        print("🛡️ No explicit keys found. Using IAM Instance Role / Default Provider Chain.")
    
    return boto3.client("bedrock-runtime", **client_kwargs)

# Singleton instance
bedrock_client = get_bedrock_client()

