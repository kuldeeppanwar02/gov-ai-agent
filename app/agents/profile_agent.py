import boto3
import json
import re
from app.config import AWS_REGION, NOVA_LITE_MODEL_ID

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def extract_profile(document_text: str) -> dict:
    """
    Use Amazon Nova Lite to extract structured user profile from a document.
    Extracts: age, gender, income, location, occupation, category, disability.
    """
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
                            "text": f"""You are an expert information extraction system for Indian government documents.

Extract the following fields from the document below. Be very precise:

- age: (integer, e.g. 25)
- gender: (exactly "Male" or "Female" or null)
- income: (annual income in INR as a number only, no symbols, e.g. 180000)
- location: (Indian state name only, e.g. "Maharashtra")
- occupation: (e.g. "Farmer", "Student", "Self-employed", "Salaried", "Unemployed")
- category: (exactly one of "SC", "ST", "OBC", "General", or null)
- disability: (true or false or null)

If any field is not mentioned in the document, return null for that field.

Return ONLY valid JSON in this exact format with no extra text:

{{
  "age": null,
  "gender": null,
  "income": null,
  "location": null,
  "occupation": null,
  "category": null,
  "disability": null
}}

Document:
{document_text[:4000]}
"""
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 400,
                "temperature": 0.1,
                "topP": 0.9
            }
        })
    )

    response_body = json.loads(response["body"].read())
    output_text = response_body["output"]["message"]["content"][0]["text"]
    print("📄 Nova Profile Output:", output_text)

    try:
        json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"⚠️ JSON parse error: {e}")

    return {
        "age": None, "gender": None, "income": None,
        "location": None, "occupation": None, "category": None, "disability": None
    }