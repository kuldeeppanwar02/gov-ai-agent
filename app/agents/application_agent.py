"""
Application Agent — Auto-Apply Simulation (Nova Act Style)
Simulates automated form-filling for government scheme portals using Playwright.
This mirrors the Nova Act approach of automating UI workflows.
"""

import json
from typing import Optional


# Scheme-specific form field mappings
SCHEME_FORM_FIELDS = {
    "PM Kisan Samman Nidhi": {
        "url": "https://pmkisan.gov.in/",
        "fields": ["farmer_name", "aadhaar", "mobile", "state", "district", "bank_account", "ifsc"],
        "estimated_time": "5-7 minutes"
    },
    "Ayushman Bharat PM-JAY": {
        "url": "https://pmjay.gov.in/",
        "fields": ["name", "aadhaar", "mobile", "state", "district", "ration_card"],
        "estimated_time": "3-5 minutes"
    },
    "PM Ujjwala Yojana": {
        "url": "https://www.pmuy.gov.in/",
        "fields": ["name", "aadhaar", "mobile", "address", "state", "bpl_card_number"],
        "estimated_time": "5-10 minutes"
    },
    "National Scholarship Portal (NSP)": {
        "url": "https://scholarships.gov.in/",
        "fields": ["student_name", "dob", "gender", "category", "income", "institution", "course", "bank_account"],
        "estimated_time": "10-15 minutes"
    },
    "Pradhan Mantri Awas Yojana (PMAY)": {
        "url": "https://pmayg.nic.in/",
        "fields": ["name", "aadhaar", "state", "district", "village", "income_category"],
        "estimated_time": "10-15 minutes"
    },
}

DEFAULT_FORM_INFO = {
    "fields": ["name", "aadhaar", "mobile", "state", "income"],
    "estimated_time": "5-10 minutes"
}


def auto_apply(scheme_name: str, profile: dict) -> dict:
    """
    Nova Act-style automated application agent.
    Navigates to the scheme portal and pre-fills form fields with user data.

    In production with Nova Act SDK:
      act = NovaAct(starting_page=scheme_url)
      act.act(f"Fill the application form with name={name}, aadhaar={aadhaar}...")

    Here we use Playwright to simulate the same workflow.
    """
    scheme_info = SCHEME_FORM_FIELDS.get(scheme_name, DEFAULT_FORM_INFO)
    apply_url = scheme_info.get("url", "#")

    # Build pre-filled field map from user profile
    name = profile.get("name", "Applicant")
    age = profile.get("age")
    gender = profile.get("gender", "")
    income = profile.get("income", 0)
    location = profile.get("location", "")
    category = profile.get("category", "General")
    disability = profile.get("disability", False)

    prefilled_data = {
        "name": name,
        "age": age,
        "gender": gender,
        "annual_income": income,
        "state": location,
        "category": category,
        "disability": disability,
    }

    # Try Playwright automation (if installed and browser available)
    playwright_status = _try_playwright_fill(apply_url, prefilled_data, scheme_name)

    return {
        "status": "ready_to_apply",
        "scheme_name": scheme_name,
        "apply_url": apply_url,
        "prefilled_fields": prefilled_data,
        "required_fields": scheme_info["fields"],
        "estimated_time": scheme_info.get("estimated_time", "5-10 minutes"),
        "automation_status": playwright_status,
        "next_steps": [
            f"1. Open {apply_url}",
            "2. Upload your Aadhaar card / income certificate",
            "3. Verify pre-filled details and submit",
            "4. Note your application reference number"
        ],
        "documents_needed": _get_documents_for_scheme(scheme_name)
    }


def _try_playwright_fill(url: str, data: dict, scheme_name: str) -> str:
    """
    Attempt Playwright-based form automation — same pattern as Nova Act.
    Returns status string.
    """
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)
            title = page.title()
            browser.close()
            return f"✅ Portal verified: '{title}' — form automation ready"
    except ImportError:
        return "⚠️ Playwright not installed — run: playwright install chromium"
    except Exception as e:
        return f"⚠️ Auto-navigation pending: {str(e)[:80]}"


def _get_documents_for_scheme(scheme_name: str) -> list[str]:
    """Return list of documents typically needed for a scheme application."""
    base_docs = ["Aadhaar Card", "Bank Account Details", "Passport Photo"]

    scheme_docs = {
        "PM Kisan Samman Nidhi": ["Land Records / Khasra-Khatauni", "Bank Passbook"],
        "Ayushman Bharat PM-JAY": ["Ration Card", "SECC Family Data Proof"],
        "PM Scholarship Scheme (PMSS)": ["Ex-Serviceman Certificate", "Mark Sheets", "Bonafide Certificate"],
        "National Scholarship Portal (NSP)": ["Income Certificate", "Caste Certificate", "Previous Year Mark Sheet"],
        "Post Matric Scholarship for SC/ST Students": ["Caste Certificate", "Income Certificate", "Institution Bonafide"],
        "PM Ujjwala Yojana": ["BPL Card / Self-declaration", "Address Proof"],
        "PM Awas Yojana (PMAY)": ["Income Certificate", "Property Documents (self-declaration of no pucca house)"],
    }

    return base_docs + scheme_docs.get(scheme_name, ["Income Certificate"])