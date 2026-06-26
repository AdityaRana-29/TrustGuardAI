"""
Explainable AI Service
Combines results from scam detector, fake news detector, and URL analyzer
into a unified, human-readable explanation with risk assessment.
"""
from typing import List, Dict
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def compute_risk_level(scam_prob: float, fake_news_prob: float, url_risks: List[Dict]) -> str:
    """Compute overall risk level from all signals."""
    max_url_risk = 0.0
    for url in url_risks:
        if url.get("risk_level") == "HIGH":
            max_url_risk = 1.0
        elif url.get("risk_level") == "MEDIUM" and max_url_risk < 0.5:
            max_url_risk = 0.5

    # Weighted combination
    combined = (scam_prob * 0.5) + (fake_news_prob * 0.3) + (max_url_risk * 100 * 0.2)

    if combined >= 60:
        return "HIGH"
    elif combined >= 35:
        return "MEDIUM"
    return "LOW"


def get_recommended_action(risk_level: str, scam_label: str, news_label: str) -> str:
    """Generate recommended action based on risk assessment."""
    if risk_level == "HIGH":
        if scam_label in ("Spam/Phishing", "Suspicious"):
            return (
                "⚠️ DO NOT click any links or share personal information. "
                "Block the sender and report as spam. "
                "If financial details were shared, contact your bank immediately."
            )
        elif news_label in ("Fake", "Likely Fake"):
            return (
                "⚠️ Do NOT share this content. "
                "Verify with trusted news sources (e.g., PIB Fact Check, BBC, NDTV). "
                "Report on platforms like SM Hoax Slayer."
            )
        return "⚠️ Exercise extreme caution. Verify the source before taking any action."

    elif risk_level == "MEDIUM":
        return (
            "🔶 Be cautious. Verify the sender's identity independently. "
            "Do not share sensitive information. Cross-check claims with official sources."
        )

    return "✅ Content appears relatively safe, but always verify important information from official sources."


def compute_overall_confidence(scam_raw: float, fake_raw: float) -> float:
    """Compute overall confidence score."""
    return round(max(scam_raw, fake_raw) * 100, 1)


def merge_reasons(scam_reasons: List[str], fake_reasons: List[str]) -> List[str]:
    """Merge and deduplicate reasons from all detectors."""
    all_reasons = []
    seen = set()

    for reason in scam_reasons + fake_reasons:
        if reason not in seen and "appears normal" not in reason.lower() and "appears credible" not in reason.lower():
            all_reasons.append(reason)
            seen.add(reason)

    return all_reasons if all_reasons else ["No specific risk indicators found"]


def build_explanation(
    original_text: str,
    detected_language: str,
    translated_text,
    scam_result: dict,
    fake_news_result: dict,
    url_risks: List[Dict],
) -> dict:
    """
    Build complete explanation combining all analysis results.
    """
    scam_prob = scam_result["scam_probability"]
    fake_prob = fake_news_result["fake_news_probability"]

    risk_level = compute_risk_level(scam_prob, fake_prob, url_risks)

    all_reasons = merge_reasons(
        scam_result.get("reasons", []),
        fake_news_result.get("reasons", []),
    )

    # Add URL-related reasons
    for url_risk in url_risks:
        for r in url_risk.get("reasons", []):
            if r not in all_reasons and "No obvious" not in r:
                all_reasons.append(f"URL risk: {r}")

    recommended_action = get_recommended_action(
        risk_level,
        scam_result["scam_label"],
        fake_news_result["news_label"],
    )

    overall_confidence = compute_overall_confidence(
        scam_result["raw_score"],
        fake_news_result["raw_score"],
    )

    # Combine suspicious keywords
    all_keywords = list(set(
        scam_result.get("suspicious_keywords", []) +
        fake_news_result.get("flagged_keywords", [])
    ))

    return {
        "input_text": original_text,
        "detected_language": detected_language,
        "translated_text": translated_text,
        "scam_probability": scam_prob,
        "fake_news_probability": fake_prob,
        "risk_level": risk_level,
        "scam_label": scam_result["scam_label"],
        "news_label": fake_news_result["news_label"],
        "reasons": all_reasons,
        "suspicious_keywords": all_keywords[:15],
        "url_risks": url_risks,
        "recommended_action": recommended_action,
        "overall_confidence": overall_confidence,
    }
