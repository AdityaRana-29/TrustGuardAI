from fastapi import APIRouter, HTTPException
from app.models.schemas import URLCheckRequest, URLRisk
from app.services.url_analyzer import analyze_url
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/check-url", response_model=URLRisk, summary="Analyze a single URL for risk")
async def check_url(request: URLCheckRequest):
    """
    Analyze a URL for phishing/scam risk indicators:
    - IP-based URLs
    - Suspicious TLDs
    - Brand impersonation
    - URL shorteners
    - Suspicious keywords
    """
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    try:
        result = analyze_url(request.url.strip())
        return URLRisk(
            url=result["url"],
            risk_level=result["risk_level"],
            risk_score=result["risk_score"],
            reasons=result["reasons"],
        )
    except Exception as e:
        logger.error(f"URL check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"URL analysis failed: {str(e)}")
