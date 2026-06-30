# 🛡️ TrustGuard AI — Fake News & Scam Detector

## 🌐 Live App → [https://trust-guard-ai-azure.vercel.app](https://trust-guard-ai-azure.vercel.app)

> AI-powered digital safety assistant that detects scams, phishing, fake news, and fraudulent content in real time.

---

## 🔗 Links

| | URL |
|---|---|
| 🌐 **Live Application** | [trust-guard-ai-azure.vercel.app](https://trust-guard-ai-azure.vercel.app) |
| ⚙️ **Backend API** | [trustguardai-backend-u82u.onrender.com](https://trustguardai-backend-u82u.onrender.com) |
| 📖 **API Docs (Swagger)** | [trustguardai-backend-u82u.onrender.com/docs](https://trustguardai-backend-u82u.onrender.com/docs) |
| 💻 **GitHub Repo** | [github.com/AdityaRana-29/TrustGuardAI](https://github.com/AdityaRana-29/TrustGuardAI) |

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🚨 Scam Detection | Detects SMS scams, phishing emails, lottery fraud, KYC scams |
| 📰 Fake News Detection | Identifies misinformation, conspiracy content, sensationalism |
| 🔗 URL Risk Analyzer | Flags phishing URLs, suspicious TLDs, brand impersonation |
| 🌐 Multilingual Support | Detects Hindi, Gujarati, Marathi + auto-translates to English |
| 📷 Screenshot OCR | Upload WhatsApp/SMS screenshots — OCR extracts & analyzes text |
| 🧠 Explainable AI | Shows *why* content is flagged, not just a probability score |

---

## 🧪 Example Test Cases

| Input | Expected Output |
|---|---|
| "Congratulations! You won ₹25,00,000. Claim now!" | Scam 98% · HIGH |
| "Your SBI account is suspended. Verify: http://sbi-xyz.tk" | Scam 95% · Phishing · HIGH |
| "Scientists discover miracle cure big pharma is hiding!" | Fake News 89% · HIGH |
| "Hi, can we meet at 3 PM for the project review?" | Safe · LOW |

---

## 🗂️ Project Structure

```
TrustGuard AI/
├── backend/               # FastAPI Python backend
│   ├── app/
│   │   ├── main.py        # FastAPI app entry
│   │   ├── routers/       # API route handlers
│   │   ├── services/      # Core AI/ML logic
│   │   ├── models/        # Pydantic schemas
│   │   └── utils/         # Logger
│   ├── run.py             # Server runner
│   └── requirements.txt
├── frontend/              # Web UI (HTML + CSS + JS)
│   ├── index.html
│   ├── style.css
│   └── app.js
└── ml/                    # ML training scripts
    ├── train_scam_model.py
    ├── train_fake_news_model.py
    └── bert_scam_detector.py
```

---

## 🤖 API Endpoints

### POST `/api/v1/analyze`
Analyze text for scams and fake news.

```json
{
  "text": "Congratulations! You won ₹25,00,000. Click here to claim."
}
```

**Response:**
```json
{
  "scam_probability": 98.5,
  "fake_news_probability": 42.1,
  "risk_level": "HIGH",
  "scam_label": "Spam/Phishing",
  "reasons": ["Prize/lottery scam keywords detected", "Urgent action requested"],
  "suspicious_keywords": ["won", "claim", "immediately"],
  "recommended_action": "⚠️ DO NOT click any links or share personal information.",
  "overall_confidence": 98.5
}
```

### POST `/api/v1/check-url`
```json
{ "url": "http://secure-bank-update.xyz/login" }
```

### POST `/api/v1/analyze-screenshot`
Upload a WhatsApp/SMS screenshot as `multipart/form-data` (field: `file`).

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.11, FastAPI, Uvicorn |
| ML / NLP | Scikit-learn, TF-IDF, BERT (HuggingFace) |
| OCR | Tesseract, pytesseract, Pillow |
| Deployment | Vercel (frontend) + Render (backend) |

---

*Built with ❤️ for a safer digital India.*
