"""
RAG Service — Government Scheme Search
Uses Amazon Titan Embeddings to embed 20+ real Indian government schemes.
At startup, all schemes are embedded and cached in memory.
On query, user profile is embedded and cosine similarity is computed.
"""

import math
from typing import Optional
from app.services.embedding_service import embed_text

# ─────────────────────────────────────────────
#  Real Indian Government Schemes Database
# ─────────────────────────────────────────────
SCHEMES_DATABASE = [
    {
        "name": "PM Jan Dhan Yojana",
        "description": "Financial inclusion scheme providing zero-balance bank accounts, RuPay debit card, and accident insurance to the unbanked population of India.",
        "eligibility": "Any Indian citizen without a bank account, especially low-income groups.",
        "apply_url": "https://pmjdy.gov.in/",
        "category": "Financial Inclusion",
        "income_limit": None,
        "for_gender": None,
    },
    {
        "name": "PM Kisan Samman Nidhi",
        "description": "Direct income support of Rs 6000 per year (in 3 installments) to small and marginal farmers owning up to 2 hectares of land.",
        "eligibility": "Small and marginal farmers with land holding. Income below Rs 3 lakh per year.",
        "apply_url": "https://pmkisan.gov.in/",
        "category": "Agriculture",
        "income_limit": 300000,
        "for_gender": None,
    },
    {
        "name": "Pradhan Mantri Awas Yojana (PMAY)",
        "description": "Affordable housing scheme providing financial assistance to build or buy a house. Covers urban and rural areas.",
        "eligibility": "EWS/LIG/MIG families without a pucca house. Annual income below Rs 18 lakh.",
        "apply_url": "https://pmayg.nic.in/",
        "category": "Housing",
        "income_limit": 1800000,
        "for_gender": None,
    },
    {
        "name": "Ayushman Bharat PM-JAY",
        "description": "World's largest health insurance scheme providing Rs 5 lakh per family per year for secondary and tertiary medical care.",
        "eligibility": "Economically weaker sections identified through SECC database. Low-income families.",
        "apply_url": "https://pmjay.gov.in/",
        "category": "Health",
        "income_limit": 250000,
        "for_gender": None,
    },
    {
        "name": "Beti Bachao Beti Padhao",
        "description": "Government scheme to address declining Child Sex Ratio and promote welfare and education of girl children.",
        "eligibility": "Families with girl children, especially in districts with low sex ratio.",
        "apply_url": "https://wcd.nic.in/bbbp-schemes",
        "category": "Women & Child",
        "income_limit": None,
        "for_gender": "Female",
    },
    {
        "name": "Sukanya Samriddhi Yojana",
        "description": "Small savings scheme for girl children with high interest rate (currently 8.2% p.a.) and tax benefits under Section 80C.",
        "eligibility": "Parents or guardians of girl children below 10 years of age.",
        "apply_url": "https://www.nsiindia.gov.in/",
        "category": "Women & Child",
        "income_limit": None,
        "for_gender": "Female",
    },
    {
        "name": "PM Scholarship Scheme (PMSS)",
        "description": "Scholarship for wards of ex-servicemen and coast guard personnel to pursue higher technical and professional education.",
        "eligibility": "Students pursuing professional/technical courses. Family income below Rs 6 lakh.",
        "apply_url": "https://scholarships.gov.in/",
        "category": "Education",
        "income_limit": 600000,
        "for_gender": None,
    },
    {
        "name": "National Scholarship Portal (NSP)",
        "description": "Umbrella scheme providing scholarships to SC, ST, OBC, minorities and economically backward students at pre-matric and post-matric levels.",
        "eligibility": "Students from SC/ST/OBC/Minority communities or low income families.",
        "apply_url": "https://scholarships.gov.in/",
        "category": "Education",
        "income_limit": 250000,
        "for_gender": None,
    },
    {
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "description": "Provides loans up to Rs 10 lakh for non-corporate, non-farm small/micro enterprises through MUDRA (Shishu, Kishore, Tarun categories).",
        "eligibility": "Small business owners, entrepreneurs, self-employed individuals.",
        "apply_url": "https://www.mudra.org.in/",
        "category": "Business & Entrepreneurship",
        "income_limit": None,
        "for_gender": None,
    },
    {
        "name": "Stand Up India",
        "description": "Facilitates bank loans between Rs 10 lakh and Rs 1 crore for SC/ST and women borrowers to set up greenfield enterprises.",
        "eligibility": "SC/ST individuals and women entrepreneurs, first-time business owners.",
        "apply_url": "https://www.standupmitra.in/",
        "category": "Business & Entrepreneurship",
        "income_limit": None,
        "for_gender": None,
    },
    {
        "name": "Mahatma Gandhi NREGA (MGNREGS)",
        "description": "Guarantees 100 days of wage employment per year to rural households whose adult members do unskilled manual work.",
        "eligibility": "Adult rural household members willing to do unskilled labor. Low income rural families.",
        "apply_url": "https://nrega.nic.in/",
        "category": "Employment",
        "income_limit": 300000,
        "for_gender": None,
    },
    {
        "name": "PM Ujjwala Yojana",
        "description": "Provides free LPG gas connections to women from Below Poverty Line (BPL) households to reduce indoor air pollution.",
        "eligibility": "Women from BPL households, not having LPG connection. Rural and urban poor.",
        "apply_url": "https://www.pmuy.gov.in/",
        "category": "Energy & Utilities",
        "income_limit": 150000,
        "for_gender": "Female",
    },
    {
        "name": "Atal Pension Yojana (APY)",
        "description": "Government-backed pension scheme for unorganized sector workers ensuring minimum Rs 1000–5000 monthly pension at age 60.",
        "eligibility": "Indian citizens between 18–40 years, especially from unorganized sector, with bank account.",
        "apply_url": "https://www.npscra.nsdl.co.in/",
        "category": "Pension & Social Security",
        "income_limit": None,
        "for_gender": None,
    },
    {
        "name": "PM Suraksha Bima Yojana",
        "description": "Accidental insurance scheme with Rs 2 lakh cover for accidental death/full disability at just Rs 20/year premium.",
        "eligibility": "Bank account holders between 18–70 years. Ideal for low-income workers.",
        "apply_url": "https://jansuraksha.gov.in/",
        "category": "Insurance",
        "income_limit": None,
        "for_gender": None,
    },
    {
        "name": "PM Jeevan Jyoti Bima Yojana",
        "description": "Life insurance scheme providing Rs 2 lakh coverage for death due to any cause at a premium of Rs 436/year.",
        "eligibility": "Bank account holders between 18–55 years. Low-income households.",
        "apply_url": "https://jansuraksha.gov.in/",
        "category": "Insurance",
        "income_limit": None,
        "for_gender": None,
    },
    {
        "name": "Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)",
        "description": "Skill development training for rural youth from poor families to get salaried jobs in organized sector.",
        "eligibility": "Rural youth between 15–35 years from poor families. SC/ST age relaxation till 45.",
        "apply_url": "https://ddugky.gov.in/",
        "category": "Skill Development",
        "income_limit": 300000,
        "for_gender": None,
    },
    {
        "name": "Startup India Scheme",
        "description": "Government initiative to promote startups with tax exemptions, funding support, fast-track exit, and IPR protection.",
        "eligibility": "DPIIT-recognized startups not older than 10 years with annual turnover below Rs 100 crore.",
        "apply_url": "https://www.startupindia.gov.in/",
        "category": "Business & Entrepreneurship",
        "income_limit": None,
        "for_gender": None,
    },
    {
        "name": "National Social Assistance Programme (NSAP)",
        "description": "Social welfare program providing pension to elderly, widows, and disabled people from BPL households.",
        "eligibility": "Elderly persons above 60, widows above 40, disabled persons with 80%+ disability from BPL families.",
        "apply_url": "https://nsap.nic.in/",
        "category": "Pension & Social Security",
        "income_limit": 150000,
        "for_gender": None,
    },
    {
        "name": "Post Matric Scholarship for SC/ST Students",
        "description": "Financial assistance for SC/ST students studying in post-matric courses to support higher education.",
        "eligibility": "SC/ST students pursuing post-matriculation studies. Parental income ceiling applies (varies by state).",
        "apply_url": "https://scholarships.gov.in/",
        "category": "Education",
        "income_limit": 250000,
        "for_gender": None,
    },
    {
        "name": "Women Entrepreneurship Platform (WEP)",
        "description": "NITI Aayog's initiative to foster women entrepreneurship by providing mentorship, finance, and market access support.",
        "eligibility": "Women entrepreneurs and aspiring women business owners across India.",
        "apply_url": "https://wep.gov.in/",
        "category": "Business & Entrepreneurship",
        "income_limit": None,
        "for_gender": "Female",
    },
    {
        "name": "PM Vishwakarma Yojana",
        "description": "Support scheme for traditional artisans and craftspeople (Vishwakarmas) with skill training, credit, and market access worth Rs 1–2 lakh.",
        "eligibility": "Artisans/craftspeople in 18 traditional trades like blacksmith, potter, carpenter, tailor etc.",
        "apply_url": "https://pmvishwakarma.gov.in/",
        "category": "Skill Development",
        "income_limit": None,
        "for_gender": None,
    },
    {
        "name": "Divyangjan Scholarship Scheme",
        "description": "Scholarships for students with disabilities (Divyangjan) to pursue higher education at top institutions.",
        "eligibility": "Students with 40%+ benchmark disability pursuing graduation or postgraduate courses.",
        "apply_url": "https://scholarships.gov.in/",
        "category": "Disability",
        "income_limit": 250000,
        "for_gender": None,
    },
]

# ─────────────────────────────────────────────
#  In-Memory Embedding Cache
# ─────────────────────────────────────────────
_scheme_embeddings: list[dict] = []
_embeddings_ready = False


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def preload_scheme_embeddings():
    """
    Called at application startup.
    Embeds all scheme descriptions and caches them in memory.
    """
    global _scheme_embeddings, _embeddings_ready
    print("🔄 Pre-loading scheme embeddings via Amazon Titan...")
    _scheme_embeddings = []
    for scheme in SCHEMES_DATABASE:
        text = f"{scheme['name']}. {scheme['description']} Eligibility: {scheme['eligibility']}"
        try:
            embedding = embed_text(text)
            _scheme_embeddings.append({"scheme": scheme, "embedding": embedding})
        except Exception as e:
            print(f"⚠️ Could not embed scheme '{scheme['name']}': {e}")
    _embeddings_ready = True
    print(f"✅ {len(_scheme_embeddings)} scheme embeddings ready.")


def find_matching_schemes(profile: dict, top_k: int = 5) -> list[dict]:
    """
    Given a user profile dict, find the most semantically relevant schemes.
    Falls back to rule-based filtering if embeddings are not ready.
    """
    # Build profile summary text for embedding
    profile_text = (
        f"User profile: age {profile.get('age')}, gender {profile.get('gender')}, "
        f"annual income Rs {profile.get('income')}, located in {profile.get('location')}, "
        f"occupation {profile.get('occupation')}, category {profile.get('category')}, "
        f"disability {profile.get('disability')}. "
        f"Looking for government schemes and benefits."
    )

    # If embeddings are loaded, use cosine similarity
    if _embeddings_ready and _scheme_embeddings:
        try:
            profile_embedding = embed_text(profile_text)
            scored = []
            for item in _scheme_embeddings:
                sim = _cosine_similarity(profile_embedding, item["embedding"])
                scored.append((sim, item["scheme"]))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [s[1] for s in scored[:top_k]]
        except Exception as e:
            print(f"⚠️ Embedding query failed, falling back to rules: {e}")

    # Fallback: rule-based filter
    income = profile.get("income") or 999999999
    gender = (profile.get("gender") or "").lower()
    results = []
    for scheme in SCHEMES_DATABASE:
        passes_income = scheme["income_limit"] is None or income <= scheme["income_limit"]
        passes_gender = scheme["for_gender"] is None or scheme["for_gender"].lower() == gender
        if passes_income and passes_gender:
            results.append(scheme)
    return results[:top_k]


def get_all_schemes() -> list[dict]:
    return SCHEMES_DATABASE
