# 🇮🇳 Gov AI Agent — Amazon Nova AI Hackathon

> AI-powered Indian government scheme eligibility assistant built with **Amazon Nova Lite** (text + vision), **Amazon Titan Embeddings** (RAG), and **Nova Act** (UI automation).

---

## 🎯 Real-World Impact

India has **750+ central government schemes** worth ₹40 lakh crore annually.
- 📊 **60% of eligible citizens** never claim their benefits due to unawareness
- 🧾 **Manual application** takes 4–8 hours per scheme
- 🌐 **800M+ people** could benefit from AI-guided scheme discovery

**Gov AI Agent reduces scheme discovery from hours to seconds, and application effort by 90%.**

---

## 🚀 What It Does

| Step | Feature | Nova Model |
|---|---|---|
| 1️⃣ | Upload Aadhaar photo, income cert image, text, or PDF | **Nova Lite (Multimodal Vision)** |
| 2️⃣ | Extract profile: age, income, gender, occupation, category | **Nova Lite (Text)** |
| 3️⃣ | RAG pipeline semantically matches 22+ real schemes | **Amazon Titan Embeddings** |
| 4️⃣ | AI explains *why* you qualify for each scheme | **Nova Lite (Reasoning)** |
| 5️⃣ | Auto-fill government portal forms | **Nova Act SDK** |
| 6️⃣ | Chat: Ask anything about schemes in natural language | **Nova Lite (Chat)** |

---

## 🏗️ Architecture

```
React Frontend
     │
     ├── POST /upload  ──► File Type Detection
     │                       ├── .jpg/.png  → Nova Lite Multimodal Vision
     │                       ├── .pdf       → pdfplumber + Nova Lite
     │                       └── .txt       → Nova Lite Text
     │                     → Titan Embeddings RAG → Nova Lite Eligibility Reasoning
     │
     ├── POST /apply   ──► Nova Act SDK → Browser Form Automation
     ├── POST /chat    ──► Nova Lite Q&A
     └── GET  /schemes ──► 22 Real Scheme Database
```

---

## 🤖 Amazon Nova Models Used

| Model | Usage |
|---|---|
| `amazon.nova-lite-v1:0` | Profile extraction (text + vision), eligibility AI reasoning, Q&A chat |
| `amazon.titan-embed-text-v2:0` | RAG — semantic scheme matching via cosine similarity |
| **Nova Act SDK** | Browser UI automation for government portal form filling |

---

## 🛠️ Setup

### Prerequisites
- Python 3.10+ · Node.js 18+ · AWS CLI configured · Bedrock access (`us-east-1`)

### Backend
```bash
cd gov-ai-agent
python -m venv venv
venv\Scripts\activate         # Windows

pip install -r requirements.txt
playwright install chromium

# Edit .env — add your S3 bucket and Nova Act API key
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install && npm start
```

App: `http://localhost:3000`

---

## 🔑 Nova Act Setup
1. Get API key from [nova-act.amazon.com](https://nova-act.amazon.com/)
2. Add to `.env`: `NOVA_ACT_API_KEY=your_key_here`
3. Nova Act will automatically navigate to and fill government portals

---

## 📄 Sample Test Document (test.txt)
```
Name: Priya Sharma
Age: 28 | Gender: Female | Annual Income: 180000
State: Maharashtra | Occupation: Farmer | Category: OBC
```
Or simply **upload your Aadhaar card photo** — Nova Vision handles it! 🖼️

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
| Skill | PM Vishwakarma |
| Disability | Divyangjan Scholarship |
| Financial | PM Jan Dhan Yojana |

---

## 🎥 Demo Video
*Upload demo: Text / Image / PDF → Profile → Schemes → Auto-Apply — #AmazonNova*

---

## 📜 License
MIT
