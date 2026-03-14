# 🇮🇳 Gov AI Agent — Amazon Nova Hackathon Submission

> AI-powered Indian government scheme eligibility assistant built with **Amazon Nova Lite**, **Titan Embeddings**, and **Nova Act-style UI automation**.

---

## 🚀 What It Does

1. **Upload a document** (Aadhaar, income cert, any text) → Nova Lite extracts your profile (age, gender, income, location, occupation, category)
2. **RAG Pipeline** → Amazon Titan Embeddings semantically match your profile against 22+ real Indian government schemes
3. **AI Eligibility Reasoning** → Nova Lite explains *why* you qualify for each scheme
4. **Auto-Apply Agent** → Nova Act-style Playwright agent pre-fills government portal forms with your data
5. **Nova Chat** → Ask any question about schemes in natural language

---

## 🏗️ Architecture

```
Frontend (React)
     │
     ├─ POST /upload  → profile_agent (Nova Lite) → eligibility_agent (Nova Lite + RAG)
     ├─ POST /apply   → application_agent (Playwright / Nova Act)
     ├─ POST /chat    → Nova Lite Q&A
     └─ GET  /schemes → RAG scheme database
     
RAG Pipeline:
  Startup → embed_text (Titan Embeddings) → cache 22 schemes in memory
  Query   → embed profile → cosine similarity → top-5 schemes → Nova Lite reasoning
```

---

## 🤖 Amazon Nova Models Used

| Model | Usage |
|---|---|
| `amazon.nova-lite-v1:0` | Profile extraction, eligibility reasoning, Q&A chat |
| `amazon.titan-embed-text-v2:0` | RAG embeddings for semantic scheme matching |

---

## 🛠️ Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- AWS credentials configured (`aws configure`)
- AWS Bedrock access enabled for `us-east-1`

### Backend
```bash
cd gov-ai-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Copy and configure .env
copy .env .env.local         # Edit S3 bucket name

# Run backend
uvicorn app.main:app --reload
```

Backend starts at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm start
```

Frontend starts at `http://localhost:3000`

---

## 📄 Sample Test Document

Create a `test.txt` file with:
```
Name: Priya Sharma
Age: 28
Gender: Female
Annual Income: 180000
State: Maharashtra
Occupation: Farmer
Category: OBC
Disability: No
```

Upload this via the web UI to see all eligible schemes.

---

## 🏛️ Government Schemes Database (22 Schemes)

| Category | Schemes |
|---|---|
| Agriculture | PM Kisan Samman Nidhi |
| Health | Ayushman Bharat PM-JAY |
| Housing | PM Awas Yojana |
| Education | PM Scholarship, NSP, Post-Matric SC/ST |
| Women | Beti Bachao, Sukanya Samriddhi, PM Ujjwala, WEP |
| Business | PM Mudra, Stand Up India, Startup India |
| Employment | MGNREGS, DDU-GKY |
| Insurance | PM Suraksha Bima, PM Jeevan Jyoti |
| Pension | Atal Pension Yojana, NSAP |
| Disability | Divyangjan Scholarship |
| Artisans | PM Vishwakarma Yojana |
| Financial | PM Jan Dhan Yojana |

---

## 🎥 Demo Video

*Coming soon — #AmazonNova*

---

## 📜 License

MIT
