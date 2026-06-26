from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, URLRisk
from app.services.scam_detector import detect_scam
from app.services.fake_news_detector import detect_fake_news
from app.services.url_analyzer import analyze_urls_in_text
from app.services.language_service import process_multilingual_text
from app.services.explainer import build_explanation
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/analyze", response_model=AnalyzeResponse, summary="Analyze text for scams and fake news")
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze a message, email, SMS, or news article for:
    - Scam/phishing indicators
    - Fake news indicators
    - URL risks
    - Overall risk level and recommended action
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(request.text) > 10000:
        raise HTTPException(status_code=400, detail="Text too long (max 10,000 characters)")

    try:
        # Step 1: Language detection and translation
        lang_result = process_multilingual_text(request.text)
        analysis_text = lang_result["analysis_text"]

        # Step 2: Scam detection
        scam_result = detect_scam(analysis_text)

        # Step 3: Fake news detection
        fake_news_result = detect_fake_news(analysis_text)

        # Step 4: URL risk analysis
        raw_url_risks = analyze_urls_in_text(analysis_text)
        url_risks = [
            URLRisk(
                url=u["url"],
                risk_level=u["risk_level"],
                risk_score=u["risk_score"],
                reasons=u["reasons"],
            )
            for u in raw_url_risks
        ]

        # Step 5: Build unified explanation
        explanation = build_explanation(
            original_text=request.text,
            detected_language=lang_result["detected_language_name"],
            translated_text=lang_result.get("translated_text"),
            scam_result=scam_result,
            fake_news_result=fake_news_result,
            url_risks=raw_url_risks,
        )

        return AnalyzeResponse(
            input_text=explanation["input_text"],
            detected_language=explanation["detected_language"],
            translated_text=explanation.get("translated_text"),
            scam_probability=explanation["scam_probability"],
            fake_news_probability=explanation["fake_news_probability"],
            risk_level=explanation["risk_level"],
            scam_label=explanation["scam_label"],
            news_label=explanation["news_label"],
            reasons=explanation["reasons"],
            suspicious_keywords=explanation["suspicious_keywords"],
            url_risks=url_risks,
            recommended_action=explanation["recommended_action"],
            overall_confidence=explanation["overall_confidence"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
