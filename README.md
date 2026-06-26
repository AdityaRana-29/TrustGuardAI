# 🛡️ TrustGuard AI — Fake News & Scam Detector

> AI-powered digital safety assistant that detects scams, phishing, fake news, and fraudulent content.
> Built for the **Tata Technologies Hackathon**.

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

## ⚙️ Setup & Run

### 1. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. (Optional) Install Tesseract for OCR

- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Ubuntu**: `sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-guj`
- **macOS**: `brew install tesseract`

### 3. Start the backend

```bash
cd backend
python run.py
```

The API will be available at: http://localhost:8000

Swagger docs: http://localhost:8000/docs

### 4. Open the frontend

Simply open `frontend/index.html` in your browser.
(Or use Live Server in VS Code)

---

## 🧪 API Endpoints

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
  "news_label": "Real",
  "reasons": [
    "Prize/lottery scam keywords detected",
    "Urgent action requested",
    "Suspicious link pattern detected",
    "Unrealistic financial reward claim"
  ],
  "suspicious_keywords": ["won", "claim", "immediately"],
  "recommended_action": "⚠️ DO NOT click any links...",
  "overall_confidence": 98.5
}
```

### POST `/api/v1/check-url`
Analyze a single URL for risk.

```json
{ "url": "http://secure-bank-update.xyz/login" }
```

### POST `/api/v1/analyze-screenshot`
Upload an image (multipart/form-data, field: `file`).

---

## 🤖 ML Training

### Train Scam Model
```bash
python ml/train_scam_model.py
```
Downloads SMS Spam Collection dataset automatically.

### Train Fake News Model
```bash
python ml/train_fake_news_model.py
```
Place `Fake.csv` and `True.csv` from Kaggle in `ml/data/` for full accuracy.
Falls back to built-in demo dataset.

### Train BERT Model (Advanced)
```bash
python ml/bert_scam_detector.py
```
Requires GPU for reasonable training time.

---

## 🌐 Example Test Cases

| Input | Expected Output |
|---|---|
| "Congratulations! You won ₹25,00,000. Claim now!" | Scam 98% · HIGH |
| "Your SBI account is suspended. Verify: http://sbi-xyz.tk" | Scam 95% · Phishing · HIGH |
| "Scientists discover miracle cure big pharma is hiding!" | Fake News 89% · HIGH |
| "Hi, can we meet at 3 PM for the project review?" | Safe · LOW |

---

## 🏆 Hackathon Highlights

- Combines **NLP + Computer Vision + OCR + Cybersecurity**
- **Explainable AI**: Shows *why* content is risky, not just a score
- **Indian context**: UPI fraud, KYC scams, regional language support
- **Production-ready**: FastAPI + modular architecture
- **Visual UI**: Dark-themed, mobile-friendly, real-time analysis

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| ML/NLP | Scikit-learn, TF-IDF, BERT (HuggingFace) |
| OCR | Tesseract, pytesseract, Pillow |
| Language | langdetect, googletrans |
| Frontend | HTML5, CSS3, Vanilla JavaScript |

---

*Built with ❤️ for a safer digital India.*
