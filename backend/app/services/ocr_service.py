"""
OCR Service
Extracts text from uploaded images (e.g., WhatsApp screenshots) using Tesseract.
"""
import io
from typing import Optional
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def extract_text_from_image(image_bytes: bytes) -> Optional[str]:
    """
    Extract text from image bytes using pytesseract.
    Supports multiple languages: English + Hindi + Gujarati.
    Returns extracted text or None if extraction fails.
    """
    try:
        from PIL import Image
        import pytesseract

        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        # Try multi-language OCR first (eng + hin + guj)
        try:
            text = pytesseract.image_to_string(image, lang="eng+hin+guj")
        except Exception:
            # Fall back to English only
            text = pytesseract.image_to_string(image, lang="eng")

        text = text.strip()
        if not text:
            logger.warning("OCR returned empty text")
            return None

        logger.info(f"OCR extracted {len(text)} characters")
        return text

    except ImportError as e:
        logger.error(f"OCR dependencies not installed: {e}")
        raise RuntimeError(
            "OCR dependencies not installed. "
            "Install Tesseract and pytesseract: pip install pytesseract Pillow"
        )
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise RuntimeError(f"Failed to extract text from image: {str(e)}")


def preprocess_image(image_bytes: bytes) -> bytes:
    """
    Preprocess image for better OCR accuracy.
    Converts to grayscale and enhances contrast.
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        import io

        image = Image.open(io.BytesIO(image_bytes))
        # Convert to grayscale
        image = image.convert("L")
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        # Apply sharpening
        image = image.filter(ImageFilter.SHARPEN)

        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}. Using original.")
        return image_bytes
