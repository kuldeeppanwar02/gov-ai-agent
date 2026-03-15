import boto3
import json
import re
from app.config import AWS_REGION, NOVA_LITE_MODEL_ID, bedrock_client
from app.services.rag_service import find_matching_schemes

bedrock = bedrock_client


def check_eligibility(profile: dict) -> list[dict]:
    """
    Use Amazon Nova Lite as an AI judge to determine which government schemes
    the user is eligible for, based on their profile. Uses RAG to pre-filter
    relevant schemes before calling Nova.
    """

    # Step 1: RAG — get top semantically relevant schemes
    candidate_schemes = find_matching_schemes(profile, top_k=10)

    # Build scheme list for the prompt
    scheme_list = "\n".join([
        f"{i+1}. {s['name']}: {s['description']} | Eligibility: {s['eligibility']}"
        for i, s in enumerate(candidate_schemes)
    ])

    profile_text = f"""
Age: {profile.get('age')}
Gender: {profile.get('gender')}
Annual Income (INR): {profile.get('income')}
Location/State: {profile.get('location')}
Occupation: {profile.get('occupation')}
Social Category: {profile.get('category')}
Disability: {profile.get('disability')}
""".strip()

    # Step 2: Ask Nova Lite to evaluate eligibility
    prompt = f"""You are an expert in Indian government welfare schemes.

Below is a citizen profile and a list of government schemes.
Carefully analyze which schemes this citizen is eligible for and explain why.

CITIZEN PROFILE:
{profile_text}

AVAILABLE SCHEMES:
{scheme_list}

For each scheme the citizen qualifies for, return a JSON entry.
Return ONLY a valid JSON array (no extra text) in this exact format:

[
  {{
    "scheme_name": "Scheme Name",
    "reason": "Brief explanation of why this citizen qualifies",
    "apply_url": "URL from scheme description",
    "category": "Category of scheme",
    "priority": "High/Medium/Low based on how well they qualify"
  }}
]

If no schemes match, return an empty array: []
"""

    try:
        response = bedrock.invoke_model(
            modelId=NOVA_LITE_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 1500,
                    "temperature": 0.2,
                    "topP": 0.9
                }
            })
        )

        response_body = json.loads(response["body"].read())
        output_text = response_body["output"]["message"]["content"][0]["text"]
        print("🤖 Nova Eligibility Output:", output_text[:500])

        # Extract JSON array from response
        json_match = re.search(r'\[.*\]', output_text, re.DOTALL)
        if json_match:
            eligible = json.loads(json_match.group())
            # Merge apply_url from our database if Nova missed it
            scheme_url_map = {s["name"]: s["apply_url"] for s in candidate_schemes}
            for item in eligible:
                if not item.get("apply_url"):
                    item["apply_url"] = scheme_url_map.get(item.get("scheme_name"), "#")
            return eligible

    except Exception as e:
        print(f"⚠️ Nova eligibility check failed: {e}")

    # Fallback — return raw RAG results without AI reasoning
    return [
        {
            "scheme_name": s["name"],
            "reason": s["eligibility"],
            "apply_url": s["apply_url"],
            "category": s["category"],
            "priority": "Medium"
        }
        for s in candidate_schemes[:5]
    ]