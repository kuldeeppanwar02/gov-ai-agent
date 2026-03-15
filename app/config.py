import os
import json
import boto3
import botocore.config
import requests
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv

load_dotenv()

def _clean_var(name: str, default: str = "") -> str:
    """Robustly clean environment variables: strip quotes, spaces, and hidden line endings."""
    val = os.getenv(name, default)
    if not val:
        return ""
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

print(f"🔧 Bedrock region: {AWS_REGION}")
print(f"📦 boto3 version: {boto3.__version__}")

key_id = AWS_ACCESS_KEY_ID if AWS_ACCESS_KEY_ID else None
secret = AWS_SECRET_ACCESS_KEY if AWS_SECRET_ACCESS_KEY else None

if key_id:
    masked_id = f"{key_id[:4]}...{key_id[-4:]}"
    print(f"🔑 Using explicit credentials: {masked_id} (Length: {len(key_id)})")
else:
    print("🛡️ No explicit keys set. Using IAM Instance Role / Default Provider Chain.")

# ─────────────────────────────────────────────────────────────────────────────
# WORKAROUND: botocore has a known bug where model IDs with colons (':')
# get double URL-encoded (%253A instead of %3A) in the canonical string,
# causing InvalidSignatureException for ALL Bedrock calls.
#
# FIX: We bypass boto3's invoke_model entirely and use `requests` + `AWS4Auth`
# which builds the URL and signature correctly without double-encoding.
# ─────────────────────────────────────────────────────────────────────────────

def _get_aws4auth():
    """Returns an AWS4Auth object for signing Bedrock HTTP requests."""
    if key_id and secret:
        return AWS4Auth(key_id, secret, AWS_REGION, "bedrock")
    else:
        # Fallback: get credentials from the boto3 default provider chain (IAM Role)
        session = boto3.Session()
        creds = session.get_credentials().get_frozen_credentials()
        return AWS4Auth(creds.access_key, creds.secret_key, AWS_REGION, "bedrock",
                        session_token=creds.token)

def bedrock_invoke(model_id: str, body: dict) -> dict:
    """
    Invoke a Bedrock model using requests + AWS4Auth to bypass botocore's
    double URL-encoding bug for model IDs containing colons.
    """
    # Build URL manually — no botocore URL serialization = no double-encoding
    url = f"https://bedrock-runtime.{AWS_REGION}.amazonaws.com/model/{model_id}/invoke"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    auth = _get_aws4auth()
    response = requests.post(url, json=body, headers=headers, auth=auth, timeout=60)
    response.raise_for_status()
    return response.json()

# Keep boto3 client for any non-Bedrock operations (e.g., S3, etc.)
def get_bedrock_client():
    """Returns boto3 bedrock-runtime client (use bedrock_invoke() for model calls)."""
    client_kwargs = {
        "region_name": AWS_REGION,
        "config": botocore.config.Config(retries={"max_attempts": 3, "mode": "standard"})
    }
    if key_id and secret:
        client_kwargs["aws_access_key_id"] = key_id
        client_kwargs["aws_secret_access_key"] = secret
    return boto3.client("bedrock-runtime", **client_kwargs)

# Keep for backward compat — but prefer bedrock_invoke() for actual API calls
bedrock_client = get_bedrock_client()
