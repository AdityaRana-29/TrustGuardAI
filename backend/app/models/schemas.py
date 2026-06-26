from pydantic import BaseModel
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    text: str
    language: Optional[str] = "auto"

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Congratulations! You won ₹25,00,000. Click here to claim immediately.",
                "language": "auto"
            }
        }


class SuspicionReason(BaseModel):
    reason: str
    confidence: float


class URLRisk(BaseModel):
    url: str
    risk_level: str  # LOW / MEDIUM / HIGH
    risk_score: float
    reasons: List[str]


class AnalyzeResponse(BaseModel):
    input_text: str
    detected_language: str
    translated_text: Optional[str] = None
    scam_probability: float
    fake_news_probability: float
    risk_level: str            # LOW / MEDIUM / HIGH
    scam_label: str            # Spam / Phishing / Normal
    news_label: str            # Fake / Likely Fake / Real
    reasons: List[str]
    suspicious_keywords: List[str]
    url_risks: List[URLRisk]
    recommended_action: str
    overall_confidence: float


class URLCheckRequest(BaseModel):
    url: str

    class Config:
        json_schema_extra = {
            "example": {
                "url": "http://secure-bank-update.xyz/login"
            }
        }
