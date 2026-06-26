from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models.schemas import AnalyzeResponse, URLRisk
from app.services.ocr_service import extract_text_from_image, preprocess_image
from app.services.scam_detector import detect_scam
from app.services.fake_news_detector import detect_fake_news
from app.services.url_analyzer import analyze_urls_in_text
from app.services.language_service import process_multilingual_text
from app.services.explainer import build_explanation
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/analyze-screenshot",
    response_model=AnalyzeResponse,
    summary="Analyze a WhatsApp/SMS screenshot for scams",
)
async def analyze_screenshot(file: UploadFile = File(...)):
    """
    Upload a screenshot (WhatsApp, SMS, email).
    The system will:
    1. Extract text using OCR
    2. Detect language
    3. Analyze for scams and fake news
    4. Return full risk assessment
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: {ALLOWED_CONTENT_TYPES}",
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    try:
        # Step 1: Preprocess and OCR
        processed_bytes = preprocess_image(image_bytes)
        extracted_text = extract_text_from_image(processed_bytes)

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from image. Ensure the image has clear, readable text.",
            )

        # Step 2: Language detection and translation
        lang_result = process_multilingual_text(extracted_text)
        analysis_text = lang_result["analysis_text"]

        # Step 3: Analysis pipeline
        scam_result = detect_scam(analysis_text)
        fake_news_result = detect_fake_news(analysis_text)
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

        explanation = build_explanation(
            original_text=extracted_text,
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
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Screenshot analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Screenshot analysis failed: {str(e)}")
