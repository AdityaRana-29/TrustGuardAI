"""
URL Risk Analyzer
Checks URLs for suspicious patterns without external API calls.
"""
import re
import math
from typing import List, Dict
from urllib.parse import urlparse
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Suspicious TLDs and domain patterns
# ---------------------------------------------------------------------------
SUSPICIOUS_TLDS = {
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click",
    ".download", ".loan", ".win", ".bid", ".stream", ".party",
    ".review", ".date", ".faith", ".accountant", ".science",
    ".trade", ".racing", ".webcam"
}

LEGITIMATE_BRANDS = [
    "google", "facebook", "amazon", "microsoft", "apple", "paypal",
    "sbi", "hdfc", "icici", "paytm", "phonepe", "gpay", "upi",
    "irdai", "sebi", "rbi", "gov", "nic", "nsdl", "epfo",
]

SUSPICIOUS_KEYWORDS_IN_URL = [
    "login", "signin", "verify", "update", "secure", "account",
    "confirm", "banking", "payment", "wallet", "prize", "winner",
    "claim", "reward", "free", "lucky", "offer", "discount",
    "kyc", "otp", "password", "credential",
]

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "buff.ly", "is.gd", "rb.gy", "cutt.ly", "short.io",
}


def _is_ip_url(url: str) -> bool:
    """Check if URL uses an IP address instead of domain name."""
    parsed = urlparse(url if url.startswith("http") else "http://" + url)
    hostname = parsed.hostname or ""
    ip_pattern = re.compile(r'^\d{1,3}(\.\d{1,3}){3}$')
    return bool(ip_pattern.match(hostname))


def _get_domain(url: str) -> str:
    parsed = urlparse(url if url.startswith("http") else "http://" + url)
    return (parsed.hostname or "").lower()


def _get_tld(domain: str) -> str:
    parts = domain.split(".")
    if len(parts) >= 2:
        return "." + parts[-1]
    return ""


def analyze_url(url: str) -> Dict:
    risk_score = 0.0
    reasons = []
    domain = _get_domain(url)
    tld = _get_tld(domain)
    url_lower = url.lower()

    # 1. IP-based URL
    if _is_ip_url(url):
        risk_score += 0.90
        reasons.append("URL uses IP address instead of domain name")

    # 2. Suspicious TLD
    if tld in SUSPICIOUS_TLDS:
        risk_score += 0.65
        reasons.append(f"Suspicious top-level domain: {tld}")

    # 3. URL shortener
    for shortener in SHORTENER_DOMAINS:
        if shortener in domain:
            risk_score += 0.55
            reasons.append("URL shortener detected — destination unknown")
            break

    # 4. Brand impersonation
    for brand in LEGITIMATE_BRANDS:
        if brand in domain and not domain.endswith(f"{brand}.com") and not domain.endswith(f"{brand}.in"):
            risk_score += 0.75
            reasons.append(f"Possible brand impersonation: '{brand}' in suspicious domain")
            break

    # 5. Suspicious keywords in URL
    for keyword in SUSPICIOUS_KEYWORDS_IN_URL:
        if keyword in url_lower:
            risk_score += 0.25
            reasons.append(f"Suspicious keyword in URL: '{keyword}'")
            break  # count once

    # 6. Excessive URL length
    if len(url) > 100:
        risk_score += 0.30
        reasons.append(f"Unusually long URL ({len(url)} characters)")

    # 7. Excessive special characters
    special_chars = len(re.findall(r'[%@!~]', url))
    if special_chars > 3:
        risk_score += 0.35
        reasons.append(f"Excessive special characters in URL ({special_chars} found)")

    # 8. Multiple subdomains
    subdomain_count = len(domain.split(".")) - 2
    if subdomain_count >= 3:
        risk_score += 0.40
        reasons.append(f"Multiple subdomains detected ({subdomain_count})")

    # 9. HTTP (not HTTPS)
    if url.startswith("http://"):
        risk_score += 0.25
        reasons.append("Insecure HTTP connection (not HTTPS)")

    # Normalise
    risk_score = min(risk_score, 0.99)
    risk_score = round(1 - math.exp(-risk_score * 1.5), 4) if risk_score > 0 else 0.0

    if not reasons:
        reasons.append("No obvious risk factors detected")

    return {
        "url": url,
        "risk_score": round(risk_score * 100, 1),
        "risk_level": _risk_level(risk_score),
        "reasons": reasons,
    }


def _risk_level(score: float) -> str:
    if score >= 0.65:
        return "HIGH"
    elif score >= 0.35:
        return "MEDIUM"
    return "LOW"


def analyze_urls_in_text(text: str) -> List[Dict]:
    url_pattern = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+'
        r'|www\.[^\s<>"{}|\\^`\[\]]+'
    )
    urls = url_pattern.findall(text)
    return [analyze_url(url) for url in urls]
