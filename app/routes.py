from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import boto3
import json

from app.services.s3_service import upload_to_s3
from app.agents.profile_agent import (
    extract_profile_from_text,
    extract_profile_from_image,
    extract_profile_from_pdf,
)
from app.agents.eligibility_agent import check_eligibility
from app.agents.application_agent import auto_apply
from app.services.rag_service import get_all_schemes
from app.config import AWS_REGION, NOVA_LITE_MODEL_ID

router = APIRouter()
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Supported file types
IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
PDF_TYPE = "application/pdf"


# ─────────────────────────────────────────────
#  POST /upload — Multimodal-aware pipeline
# ─────────────────────────────────────────────
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts text (.txt), images (.jpg/.png — Aadhaar, income cert photos),
    and PDFs. Automatically routes to the correct extractor.
    """
    try:
        content = await file.read()
        content_type = file.content_type or ""
        filename = file.filename or ""

        # Detect file type
        is_image = (
            content_type in IMAGE_TYPES
            or filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        )
        is_pdf = (
            content_type == PDF_TYPE
            or filename.lower().endswith(".pdf")
        )

        # ── Route to correct extractor ──────
        if is_image:
            profile = extract_profile_from_image(content, content_type or "image/jpeg")
            input_mode = "image (Nova Lite Multimodal)"
        elif is_pdf:
            profile = extract_profile_from_pdf(content)
            input_mode = "pdf (pdfplumber + Nova Lite)"
        else:
            # Plain text
            try:
                text_content = content.decode("utf-8")
            except Exception:
                text_content = content.decode("latin-1")
            if len(text_content.strip()) < 5:
                raise HTTPException(status_code=400, detail="Document is too short or empty.")
            profile = extract_profile_from_text(text_content)
            input_mode = "text (Nova Lite)"

        # Upload to S3
        file.file.seek(0)
        try:
            s3_url = upload_to_s3(file)
        except Exception as e:
            s3_url = f"s3-upload-skipped: {str(e)[:60]}"

        # Check eligibility
        eligible_schemes = check_eligibility(profile)

        return {
            "profile": profile,
            "eligible_schemes": eligible_schemes,
            "s3_url": s3_url,
            "input_mode": input_mode,
            "total_schemes_found": len(eligible_schemes)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# ─────────────────────────────────────────────
#  POST /apply — Nova Act auto-apply
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
#  POST /chat — Nova Lite Q&A
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    profile: dict = {}


@router.post("/chat")
async def chat_with_nova(request: ChatRequest):
    try:
        context = ""
        if request.profile:
            context = (
                f"\nUser profile context: Age={request.profile.get('age')}, "
                f"Gender={request.profile.get('gender')}, "
                f"Income=₹{request.profile.get('income')}, "
                f"State={request.profile.get('location')}, "
                f"Occupation={request.profile.get('occupation')}, "
                f"Category={request.profile.get('category')}.\n"
            )

        prompt = f"""You are a helpful AI assistant specializing in Indian government welfare schemes.
Help citizens understand eligibility, benefits, application process, and required documents.
{context}
Answer clearly. Mention specific scheme names and steps where relevant.

Question: {request.message}"""

        response = bedrock.invoke_model(
            modelId=NOVA_LITE_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"maxTokens": 800, "temperature": 0.7, "topP": 0.9}
            })
        )
        rb = json.loads(response["body"].read())
        answer = rb["output"]["message"]["content"][0]["text"]
        return {"reply": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


# ─────────────────────────────────────────────
#  GET /schemes — All schemes in database
# ─────────────────────────────────────────────
@router.get("/schemes")
async def list_all_schemes():
    schemes = get_all_schemes()
    return {"total": len(schemes), "schemes": schemes}


# ─────────────────────────────────────────────
#  GET /health — Quick health check
# ─────────────────────────────────────────────
@router.get("/health")
async def health():
    return {"status": "ok", "nova_model": NOVA_LITE_MODEL_ID}