import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# AWS Settings
AWS_REGION = os.getenv("AWS_REGION", "us-east-1").strip().strip('"').strip("'")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "").strip().strip('"').strip("'")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip().strip('"').strip("'")

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
    print(f"🔧 Initializing Bedrock client in {AWS_REGION}...")
    
    # Debug: Masked keys to verify they are loaded
    masked_key = f"{AWS_ACCESS_KEY_ID[:4]}...{AWS_ACCESS_KEY_ID[-4:]}" if len(AWS_ACCESS_KEY_ID) > 8 else "NOT_SET"
    print(f"🔑 AWS_ACCESS_KEY_ID: {masked_key}")
    
    return boto3.client(
        "bedrock-runtime",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID if AWS_ACCESS_KEY_ID else None,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY if AWS_SECRET_ACCESS_KEY else None,
    )

# Singleton instance
bedrock_client = get_bedrock_client()

