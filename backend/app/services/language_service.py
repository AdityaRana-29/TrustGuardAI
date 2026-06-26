"""
Language Detection & Translation Service
Detects language of input text and translates to English for analysis.
Supports English, Hindi, Gujarati, and other Indian languages.
"""
from typing import Tuple
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
    "mr": "Marathi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
    "unknown": "Unknown",
}


def detect_language(text: str) -> str:
    """Detect language code of the given text."""
    try:
        from langdetect import detect
        lang = detect(text)
        return lang
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return "en"


def translate_to_english(text: str, src_lang: str) -> Tuple[str, bool]:
    """
    Translate text to English.
    Returns (translated_text, was_translated).
    Falls back to original text if translation fails.
    """
    if src_lang == "en":
        return text, False

    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source=src_lang, target="en").translate(text)
        return translated, True
    except ImportError:
        pass

    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src=src_lang, dest="en")
        return result.text, True
    except Exception as e:
        logger.warning(f"Translation failed: {e}. Using original text.")
        return text, False


def get_language_name(lang_code: str) -> str:
    return LANGUAGE_NAMES.get(lang_code, lang_code.upper())


def process_multilingual_text(text: str) -> dict:
    """
    Detect language, translate if needed, return enriched dict.
    """
    lang_code = detect_language(text)
    lang_name = get_language_name(lang_code)

    translated_text, was_translated = translate_to_english(text, lang_code)

    return {
        "original_text": text,
        "detected_language_code": lang_code,
        "detected_language_name": lang_name,
        "translated_text": translated_text if was_translated else None,
        "analysis_text": translated_text,  # text to pass to detectors
        "was_translated": was_translated,
    }
