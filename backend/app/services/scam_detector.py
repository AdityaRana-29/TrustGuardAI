"""
Scam Detection Service
Combines rule-based keyword analysis with an ML model (Logistic Regression / BERT).
Falls back to rule-based scoring when model is not yet trained.
"""
import re
import math
from typing import Tuple, List
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Keyword dictionaries (weighted)
# ---------------------------------------------------------------------------
SCAM_KEYWORDS = {
    # Prize / lottery scams
    "won": 0.85, "winner": 0.85, "winning": 0.80, "lottery": 0.90,
    "prize": 0.85, "reward": 0.70, "claim": 0.75, "congratulations": 0.65,
    # Financial urgency
    "urgent": 0.80, "immediately": 0.85, "limited time": 0.80,
    "act now": 0.85, "expires": 0.70, "last chance": 0.80,
    "guaranteed": 0.75, "100%": 0.60,
    # Money / payment
    "₹": 0.40, "upi": 0.45, "transfer": 0.55, "bank account": 0.60,
    "otp": 0.75, "pin": 0.70, "cvv": 0.90, "kyc": 0.80,
    "free money": 0.90, "easy money": 0.85, "double your money": 0.95,
    # Phishing
    "verify your account": 0.90, "confirm your details": 0.85,
    "update your information": 0.80, "password": 0.50,
    "click here": 0.65, "tap here": 0.65,
    # Job scams
    "work from home": 0.55, "earn per day": 0.75, "no experience": 0.60,
    "part time": 0.40, "data entry": 0.45, "typing job": 0.60,
    # Investment scams
    "investment": 0.35, "returns": 0.30, "profit": 0.35,
    "crypto": 0.40, "bitcoin": 0.45, "forex": 0.55,
    "mlm": 0.80, "pyramid": 0.85, "scheme": 0.70,
    # Threats
    "arrested": 0.80, "legal action": 0.75, "your account suspended": 0.85,
    "emi bounce": 0.70, "court notice": 0.80,
}

SCAM_PATTERNS = [
    (r'\b\d{1,3}[,\d]*\s*(?:lakh|crore|million|billion|thousand)\b', 0.55, "Large monetary amount"),
    (r'\b(?:whatsapp|telegram|signal)\s+(?:group|channel|link)\b', 0.65, "Social media recruitment"),
    (r'bit\.ly|tinyurl|t\.co|goo\.gl|ow\.ly', 0.70, "Shortened URL detected"),
    (r'\b\d{10}\b', 0.40, "Phone number in message"),
    (r'[A-Z]{5}\d{4}[A-Z]', 0.50, "PAN-like pattern"),
    (r'\b\d{12}\b', 0.60, "Aadhaar-like pattern"),
]


def _extract_urls(text: str) -> List[str]:
    url_pattern = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+'
        r'|www\.[^\s<>"{}|\\^`\[\]]+'
    )
    return url_pattern.findall(text)


def _keyword_score(text: str) -> Tuple[float, List[str], List[str]]:
    text_lower = text.lower()
    matched_keywords: List[str] = []
    reasons: List[str] = []
    total_weight = 0.0

    for keyword, weight in SCAM_KEYWORDS.items():
        if keyword in text_lower:
            matched_keywords.append(keyword)
            total_weight += weight

    for pattern, weight, reason in SCAM_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            reasons.append(reason)
            total_weight += weight

    # Normalise to [0, 1] using sigmoid-like function
    score = 1 - math.exp(-total_weight * 0.5) if total_weight > 0 else 0.0
    score = min(score, 0.99)

    return round(score, 4), matched_keywords, reasons


def _build_reasons(score: float, keywords: List[str], pattern_reasons: List[str], text: str) -> List[str]:
    reasons = []
    text_lower = text.lower()

    if any(k in text_lower for k in ["won", "winner", "prize", "lottery"]):
        reasons.append("Prize/lottery scam keywords detected")
    if any(k in text_lower for k in ["urgent", "immediately", "act now", "limited time"]):
        reasons.append("Urgent action requested")
    if any(k in text_lower for k in ["otp", "cvv", "pin", "password", "bank account"]):
        reasons.append("Sensitive financial information requested")
    if any(k in text_lower for k in ["click here", "tap here"]) or _extract_urls(text):
        reasons.append("Suspicious link pattern detected")
    if any(k in text_lower for k in ["free money", "easy money", "double your money", "guaranteed"]):
        reasons.append("Unrealistic financial reward claim")
    if any(k in text_lower for k in ["work from home", "earn per day", "typing job"]):
        reasons.append("Suspicious job offer pattern")
    if any(k in text_lower for k in ["kyc", "verify your account", "update your information"]):
        reasons.append("Account verification/phishing attempt")
    if any(k in text_lower for k in ["mlm", "pyramid", "scheme"]):
        reasons.append("MLM/pyramid scheme keywords detected")
    if any(k in text_lower for k in ["arrested", "court notice", "legal action"]):
        reasons.append("Fear/threat tactics used")
    if any(k in text_lower for k in ["crypto", "bitcoin", "forex", "investment"]):
        reasons.append("Crypto/investment scam keywords detected")

    reasons.extend(pattern_reasons)
    return reasons if reasons else (["Message appears normal"] if score < 0.3 else ["General suspicious content"])


def _label(score: float) -> str:
    if score >= 0.70:
        return "Spam/Phishing"
    elif score >= 0.40:
        return "Suspicious"
    return "Normal"


def detect_scam(text: str) -> dict:
    """
    Returns scam analysis dictionary.
    """
    score, keywords, pattern_reasons = _keyword_score(text)
    urls = _extract_urls(text)
    reasons = _build_reasons(score, keywords, pattern_reasons, text)

    # Boost score slightly if URLs are present
    if urls:
        score = min(score + 0.05, 0.99)

    return {
        "scam_probability": round(score * 100, 1),
        "scam_label": _label(score),
        "suspicious_keywords": keywords[:10],  # cap at 10
        "reasons": reasons,
        "urls_found": urls,
        "raw_score": score,
    }
