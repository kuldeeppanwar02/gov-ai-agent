import boto3
import json
import re
import base64
from app.config import AWS_REGION, NOVA_LITE_MODEL_ID, bedrock_client

bedrock = bedrock_client


def extract_profile_from_text(document_text: str) -> dict:
    """Extract profile from plain text using Nova Lite."""
    prompt = _build_extraction_prompt(f"Document Text:\n{document_text[:4000]}")
    return _call_nova(prompt)


def extract_profile_from_image(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    """
    Extract profile from an IMAGE (Aadhaar card, income cert photo, etc.)
    using Amazon Nova Lite's MULTIMODAL vision capability.
    """
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    response = bedrock.invoke_model(
        modelId=NOVA_LITE_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "image": {
                                "format": media_type.split("/")[-1],  # jpeg / png
                                "source": {
                                    "bytes": image_b64
                                }
                            }
                        },
                        {
                            "text": _build_extraction_prompt("(See the image provided above)")
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0.1,
                "topP": 0.9
            }
        })
    )

    response_body = json.loads(response["body"].read())
    output_text = response_body["output"]["message"]["content"][0]["text"]
    print("📸 Nova Multimodal Output:", output_text)
    return _parse_json(output_text)


def extract_profile_from_pdf(pdf_bytes: bytes) -> dict:
    """Extract profile from a PDF file using pdfplumber + Nova Lite."""
    try:
        import pdfplumber
        import io
        full_text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages[:5]:   # Read first 5 pages max
                full_text += (page.extract_text() or "") + "\n"
        if full_text.strip():
            return extract_profile_from_text(full_text)
    except ImportError:
        print("⚠️ pdfplumber not installed, treating PDF as binary.")
    except Exception as e:
        print(f"⚠️ PDF parse error: {e}")

    return _empty_profile()


def extract_profile(document_text: str) -> dict:
    """Backwards-compatible text extraction entry point."""
    return extract_profile_from_text(document_text)


# ── Shared helpers ─────────────────────────────
def _build_extraction_prompt(content_description: str) -> str:
    return f"""You are an expert information extraction system for Indian government documents.

Extract the following fields. Be precise:
- age: (integer only, e.g. 25)
- gender: (exactly "Male" or "Female" or null)
- income: (annual income in INR as a plain number, e.g. 180000)
- location: (Indian state name only, e.g. "Maharashtra")
- occupation: (e.g. "Farmer", "Student", "Self-employed", "Salaried", "Unemployed")
- category: (exactly "SC", "ST", "OBC", or "General" — or null)
- disability: (true or false or null)

Return ONLY valid JSON — no explanation, no markdown:

{{
  "age": null,
  "gender": null,
  "income": null,
  "location": null,
  "occupation": null,
  "category": null,
  "disability": null
}}

{content_description}
"""


def _call_nova(prompt: str) -> dict:
    try:
        response = bedrock.invoke_model(
            modelId=NOVA_LITE_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"maxTokens": 400, "temperature": 0.1, "topP": 0.9}
            })
        )
        response_body = json.loads(response["body"].read())
        output_text = response_body["output"]["message"]["content"][0]["text"]
        print("📄 Nova Profile Output:", output_text[:200])
        return _parse_json(output_text)
    except Exception as e:
        print(f"⚠️ Nova call failed: {e}")
        return _empty_profile()


def _parse_json(text: str) -> dict:
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"⚠️ JSON parse error: {e}")
    return _empty_profile()


def _empty_profile() -> dict:
    return {
        "age": None, "gender": None, "income": None,
        "location": None, "occupation": None,
        "category": None, "disability": None
    }