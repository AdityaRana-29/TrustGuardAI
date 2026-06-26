"""
Fake News Detection Service
Rule-based + keyword analysis with ML-ready architecture.
Checks for sensationalist language, unverified claims, emotional manipulation.
"""
import re
import math
from typing import Tuple, List
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Fake news indicator keywords (weighted)
# ---------------------------------------------------------------------------
FAKE_NEWS_KEYWORDS = {
    # Sensationalism
    "breaking": 0.45, "shocking": 0.60, "unbelievable": 0.65,
    "you won't believe": 0.80, "mind-blowing": 0.65, "explosive": 0.60,
    "bombshell": 0.65, "jaw-dropping": 0.60, "viral": 0.35,
    # Unverified claim phrases
    "sources say": 0.55, "reportedly": 0.40, "allegedly": 0.40,
    "rumors": 0.55, "rumour": 0.55, "whispers": 0.50,
    "anonymous source": 0.65, "insider says": 0.70,
    "it is claimed": 0.60, "claimed to": 0.55,
    # Conspiracy language
    "deep state": 0.85, "they don't want you to know": 0.90,
    "mainstream media won't cover": 0.90, "hidden truth": 0.85,
    "cover-up": 0.80, "secret agenda": 0.85, "illuminati": 0.85,
    "government hiding": 0.85, "suppressed": 0.70,
    # Medical misinformation
    "miracle cure": 0.90, "doctors hate": 0.90, "big pharma": 0.75,
    "banned by doctors": 0.85, "cures cancer": 0.80, "100% effective": 0.75,
    "natural remedy": 0.30,
    # Political misinformation
    "rigged": 0.65, "stolen election": 0.75, "fake ballot": 0.80,
    "election fraud": 0.70, "corrupt media": 0.70,
    # Emotional manipulation
    "must share": 0.65, "share before deleted": 0.85,
    "forward to everyone": 0.75, "before it's too late": 0.70,
    "wake up": 0.55, "open your eyes": 0.60,
    # False statistics
    "100% proven": 0.80, "scientifically proven": 0.45,
    "studies show": 0.25, "research proves": 0.30,
}

FAKE_NEWS_PATTERNS = [
    (r'(?:click|tap|share|forward)\s+(?:now|immediately|fast|before)', 0.65, "Urgency to share/forward"),
    (r'(?:ban|remove|deleted)\s+(?:this|soon|immediately)', 0.70, "Claim of imminent removal"),
    (r'\b(?:100|99)\s*%\s*(?:sure|proven|confirmed|effective)\b', 0.75, "Absolute certainty claim"),
    (r'(?:WhatsApp|Telegram|Facebook)\s+(?:forward|share|spread)', 0.60, "Social media forwarding instruction"),
    (r'#\w+', 0.15, "Hashtag usage"),
    (r'\b(?:PM|CM|President|Minister)\s+(?:arrested|dead|resigned|exposed)\b', 0.80, "Unverified political claim"),
]

CREDIBILITY_BOOSTERS = {
    "according to": -0.15, "government announced": -0.20,
    "official statement": -0.25, "press release": -0.20,
    "confirmed by": -0.15, "verified": -0.10,
    "source: ": -0.10, "published in": -0.15,
}


def _keyword_score(text: str) -> Tuple[float, List[str]]:
    text_lower = text.lower()
    total_weight = 0.0
    matched: List[str] = []

    for keyword, weight in FAKE_NEWS_KEYWORDS.items():
        if keyword in text_lower:
            matched.append(keyword)
            total_weight += weight

    for pattern, weight, _ in FAKE_NEWS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            total_weight += weight

    # Reduce score for credibility boosters
    for phrase, reduction in CREDIBILITY_BOOSTERS.items():
        if phrase in text_lower:
            total_weight += reduction  # reduction is negative

    total_weight = max(total_weight, 0.0)
    score = 1 - math.exp(-total_weight * 0.45) if total_weight > 0 else 0.0
    score = min(score, 0.99)

    return round(score, 4), matched


def _build_reasons(score: float, keywords: List[str], text: str) -> List[str]:
    reasons = []
    text_lower = text.lower()

    if any(k in text_lower for k in ["shocking", "unbelievable", "you won't believe", "jaw-dropping"]):
        reasons.append("Sensationalist headline language detected")
    if any(k in text_lower for k in ["sources say", "reportedly", "allegedly", "anonymous source"]):
        reasons.append("Unverified/anonymous sourcing")
    if any(k in text_lower for k in ["deep state", "cover-up", "they don't want you to know", "hidden truth"]):
        reasons.append("Conspiracy theory language detected")
    if any(k in text_lower for k in ["miracle cure", "doctors hate", "cures cancer", "banned by doctors"]):
        reasons.append("Medical misinformation indicators")
    if any(k in text_lower for k in ["rigged", "stolen election", "election fraud"]):
        reasons.append("Unverified political claim")
    if any(k in text_lower for k in ["must share", "share before deleted", "forward to everyone"]):
        reasons.append("Emotional manipulation to share content")
    if any(k in text_lower for k in ["100% proven", "100% effective", "100% sure"]):
        reasons.append("Absolute certainty claim (unusual in genuine reporting)")

    for pattern, _, reason in FAKE_NEWS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if reason not in reasons:
                reasons.append(reason)

    return reasons if reasons else (["Content appears credible"] if score < 0.3 else ["General misinformation indicators"])


def _label(score: float) -> str:
    if score >= 0.70:
        return "Fake"
    elif score >= 0.40:
        return "Likely Fake"
    return "Real"


def detect_fake_news(text: str) -> dict:
    score, keywords = _keyword_score(text)
    reasons = _build_reasons(score, keywords, text)

    return {
        "fake_news_probability": round(score * 100, 1),
        "news_label": _label(score),
        "reasons": reasons,
        "flagged_keywords": keywords[:10],
        "raw_score": score,
    }
