import os
from dotenv import load_dotenv

load_dotenv()

# AWS Settings
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

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
