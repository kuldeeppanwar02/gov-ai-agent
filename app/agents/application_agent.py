"""
Application Agent — Real Nova Act Integration
Uses the official `nova-act` SDK to automate browser-based government form filling.
Falls back to pre-fill data preparation if Nova Act is unavailable.

Nova Act SDK: pip install nova-act
Docs: https://nova-act.amazon.com/
"""

import os
from typing import Optional


SCHEME_FORM_FIELDS = {
    "PM Kisan Samman Nidhi": {
        "url": "https://pmkisan.gov.in/",
        "fields": ["farmer_name", "aadhaar", "mobile", "state", "district", "bank_account", "ifsc"],
        "estimated_time": "5-7 minutes",
        "nova_act_steps": [
            "Navigate to the PM Kisan self-registration page",
            "Click on 'New Farmer Registration'",
            "Fill in the Aadhaar number field",
            "Select the state from dropdown",
            "Fill personal details: name, mobile number",
            "Fill bank details: account number and IFSC code",
            "Submit the form and capture the registration number"
        ]
    },
    "Ayushman Bharat PM-JAY": {
        "url": "https://bis.pmjay.gov.in/BIS/selfprintCard",
        "fields": ["name", "aadhaar", "mobile", "state", "district", "ration_card"],
        "estimated_time": "3-5 minutes",
        "nova_act_steps": [
            "Go to the Ayushman Bharat eligibility check page",
            "Enter mobile number and verify with OTP",
            "Search for family eligibility by Aadhaar or ration card",
            "Download the Ayushman card if eligible"
        ]
    },
    "National Scholarship Portal (NSP)": {
        "url": "https://scholarships.gov.in/",
        "fields": ["student_name", "dob", "gender", "category", "income", "institution", "course"],
        "estimated_time": "10-15 minutes",
        "nova_act_steps": [
            "Register as a new student applicant on NSP",
            "Fill academic details: institution, course, year",
            "Enter personal details: name, DOB, category, income",
            "Upload scanned documents: income certificate, mark sheet",
            "Submit application and note the application ID"
        ]
    },
}

DEFAULT_SCHEME = {
    "fields": ["name", "aadhaar", "mobile", "state", "income"],
    "estimated_time": "5-10 minutes",
    "nova_act_steps": [
        "Navigate to scheme portal",
        "Fill personal details from profile",
        "Upload required documents",
        "Submit application"
    ]
}


def auto_apply(scheme_name: str, profile: dict) -> dict:
    """
    Main entry point. Tries real Nova Act first, falls back to pre-fill prep.
    """
    scheme_info = SCHEME_FORM_FIELDS.get(scheme_name, DEFAULT_SCHEME)
    apply_url = scheme_info.get("url", "#")

    prefilled_data = _build_prefill(profile)

    # Attempt real Nova Act automation
    nova_result = _try_nova_act(apply_url, prefilled_data, scheme_name, scheme_info)

    return {
        "status": "ready_to_apply",
        "scheme_name": scheme_name,
        "apply_url": apply_url,
        "prefilled_fields": prefilled_data,
        "required_fields": scheme_info["fields"],
        "estimated_time": scheme_info.get("estimated_time", "5-10 minutes"),
        "automation_status": nova_result["status"],
        "automation_detail": nova_result["detail"],
        "nova_act_steps": scheme_info.get("nova_act_steps", []),
        "next_steps": [
            f"1. Open {apply_url}",
            "2. Upload Aadhaar card / income certificate",
            "3. Verify pre-filled details and submit",
            "4. Note your application reference number"
        ],
        "documents_needed": _get_documents(scheme_name)
    }


def _try_nova_act(url: str, data: dict, scheme_name: str, scheme_info: dict) -> dict:  # noqa
    """
    Try real Nova Act SDK automation.
    Supports two auth methods:
      1. AWS IAM (default) — uses existing AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
      2. Nova Act API Key  — set NOVA_ACT_API_KEY in .env (optional override)
    """
    NOVA_ACT_API_KEY = os.getenv("NOVA_ACT_API_KEY", "")
    AWS_REGION       = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY   = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_KEY   = os.getenv("AWS_SECRET_ACCESS_KEY", "")

    steps = scheme_info.get("nova_act_steps", ["Fill the application form with user data"])
    instruction = (
        f"Help the user apply for the {scheme_name} government scheme. "
        f"User profile: name={data.get('name')}, age={data.get('age')}, "
        f"gender={data.get('gender')}, income={data.get('annual_income')}, "
        f"state={data.get('state')}, category={data.get('category')}. "
        "Steps: " + " | ".join(steps) +
        " Pre-fill all form fields with the profile data above."
    )

    try:
        from nova_act import NovaAct

        # ── Auth Method 1: AWS IAM (preferred) ──────────────────────────
        # Uses existing AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY from .env
        if AWS_ACCESS_KEY and AWS_SECRET_KEY:
            nova_kwargs = {
                "starting_page": url,
                "aws_access_key_id": AWS_ACCESS_KEY,
                "aws_secret_access_key": AWS_SECRET_KEY,
                "aws_region": AWS_REGION,
                "headless": True,
            }
            auth_used = "AWS IAM"

        # ── Auth Method 2: Nova Act API Key (optional override) ──────────
        elif NOVA_ACT_API_KEY:
            nova_kwargs = {
                "starting_page": url,
                "api_key": NOVA_ACT_API_KEY,
                "headless": True,
            }
            auth_used = "Nova Act API Key"

        else:
            return {
                "status": "⚠️ No auth configured",
                "detail": "Add AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY to .env"
            }

        with NovaAct(**nova_kwargs) as agent:
            result = agent.act(instruction)
            detail_text = str(result) if result else "Form filled successfully"
            return {
                "status": f"✅ Nova Act complete (auth: {auth_used})",
                "detail": detail_text[:300]
            }

    except ImportError:
        return {
            "status": "⚠️ nova-act not installed",
            "detail": "Run: pip install nova-act"
        }
    except Exception as e:
        return _try_playwright_verify(url, e)



def _try_playwright_verify(url: str, prev_error: Exception) -> dict:
    """Fallback: Playwright portal verification."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)
            title = page.title()
            browser.close()
            return {
                "status": f"✅ Portal verified via browser: '{title}'",
                "detail": "Nova Act API key required for full automation"
            }
    except Exception as e2:
        return {
            "status": "📋 Manual application mode",
            "detail": "All form fields pre-filled below — open the portal and copy these values"
        }


def _build_prefill(profile: dict) -> dict:
    return {
        "name": profile.get("name", "Applicant"),
        "age": profile.get("age"),
        "gender": profile.get("gender", ""),
        "annual_income": profile.get("income", 0),
        "state": profile.get("location", ""),
        "category": profile.get("category", "General"),
        "disability": profile.get("disability", False),
    }


def _get_documents(scheme_name: str) -> list:
    base = ["Aadhaar Card", "Bank Account Details", "Passport Photo"]
    extra = {
        "PM Kisan Samman Nidhi": ["Land Records / Khasra-Khatauni", "Bank Passbook"],
        "Ayushman Bharat PM-JAY": ["Ration Card", "SECC Family Data Proof"],
        "National Scholarship Portal (NSP)": ["Income Certificate", "Caste Certificate", "Mark Sheet"],
        "PM Ujjwala Yojana": ["BPL Card / Self-declaration", "Address Proof"],
        "Post Matric Scholarship for SC/ST Students": ["Caste Certificate", "Income Certificate", "Bonafide Certificate"],
        "PM Scholarship Scheme (PMSS)": ["Ex-Serviceman Certificate", "Mark Sheets", "Bonafide Certificate"],
        "Pradhan Mantri Awas Yojana (PMAY)": ["Income Certificate", "Self-Declaration (No Pucca House)"],
    }
    return base + extra.get(scheme_name, ["Income Certificate"])