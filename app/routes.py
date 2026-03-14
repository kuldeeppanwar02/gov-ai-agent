from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import boto3
import json

from app.services.s3_service import upload_to_s3
from app.agents.profile_agent import extract_profile
from app.agents.eligibility_agent import check_eligibility
from app.agents.application_agent import auto_apply
from app.services.rag_service import get_all_schemes
from app.config import AWS_REGION, NOVA_LITE_MODEL_ID

router = APIRouter()
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


# ─────────────────────────────────────────────
#  POST /upload — Main pipeline
# ─────────────────────────────────────────────
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # 1. Read file content
        content = await file.read()
        try:
            text_content = content.decode("utf-8")
        except Exception:
            text_content = content.decode("latin-1")

        if len(text_content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Document is too short or empty.")

        # 2. Upload to S3
        file.file.seek(0)
        try:
            s3_url = upload_to_s3(file)
        except Exception as e:
            s3_url = f"s3-upload-skipped: {str(e)[:60]}"

        # 3. Extract profile via Nova Lite
        profile = extract_profile(text_content)

        # 4. Check eligibility via Nova Lite + RAG
        eligible_schemes = check_eligibility(profile)

        return {
            "profile": profile,
            "eligible_schemes": eligible_schemes,
            "s3_url": s3_url,
            "total_schemes_found": len(eligible_schemes)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# ─────────────────────────────────────────────
#  POST /apply — Auto-apply to a scheme
# ─────────────────────────────────────────────
class ApplyRequest(BaseModel):
    scheme_name: str
    profile: dict


@router.post("/apply")
async def apply_to_scheme(request: ApplyRequest):
    try:
        result = auto_apply(request.scheme_name, request.profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-apply failed: {str(e)}")


# ─────────────────────────────────────────────
#  POST /chat — Ask Nova about schemes
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    profile: dict = {}


@router.post("/chat")
async def chat_with_nova(request: ChatRequest):
    try:
        context = ""
        if request.profile:
            context = f"""
User profile context:
- Age: {request.profile.get('age')}
- Gender: {request.profile.get('gender')}
- Income: Rs {request.profile.get('income')}
- Location: {request.profile.get('location')}
- Occupation: {request.profile.get('occupation')}
- Category: {request.profile.get('category')}
"""

        prompt = f"""You are a helpful AI assistant specializing in Indian government welfare schemes and benefits.
You help citizens understand and navigate government schemes, eligibility, and application processes.
{context}
Answer the following question clearly and helpfully. If relevant, mention specific scheme names, eligibility criteria, and how to apply.

Question: {request.message}
"""

        response = bedrock.invoke_model(
            modelId=NOVA_LITE_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 800,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            })
        )
        response_body = json.loads(response["body"].read())
        answer = response_body["output"]["message"]["content"][0]["text"]
        return {"reply": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


# ─────────────────────────────────────────────
#  GET /schemes — List all available schemes
# ─────────────────────────────────────────────
@router.get("/schemes")
async def list_all_schemes():
    schemes = get_all_schemes()
    return {"total": len(schemes), "schemes": schemes}