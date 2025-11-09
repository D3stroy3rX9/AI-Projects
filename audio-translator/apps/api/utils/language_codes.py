"""
Language code mappings and utilities
"""
from typing import Dict, Optional


# Whisper language codes to LibreTranslate codes
# Most are the same, but this mapping handles any differences
WHISPER_TO_LIBRETRANSLATE: Dict[str, str] = {
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "pt": "pt",
    "ru": "ru",
    "zh": "zh",  # Whisper uses "zh" for Chinese
    "ja": "ja",
    "ko": "ko",
    "ar": "ar",
    "hi": "hi",
    "nl": "nl",
    "pl": "pl",
    "tr": "tr",
    "vi": "vi",
    "th": "th",
    "id": "id",
    "sv": "sv",
    "no": "no",
    "da": "da",
    "fi": "fi",
    "el": "el",
    "he": "iw",  # Whisper: he, LibreTranslate: iw (Hebrew)
    "cs": "cs",
    "ro": "ro",
    "hu": "hu",
    "uk": "uk",
    "fa": "fa",
    "sk": "sk",
    "bg": "bg",
    "ca": "ca",
    "hr": "hr",
    "sr": "sr",
    "bn": "bn",
    "ta": "ta",
    "te": "te",
    "mr": "mr",
    "ml": "ml",
    "kn": "kn",
    "gu": "gu",
    "ur": "ur",
    "ms": "ms",
}


# Common language code to full name mapping
LANGUAGE_NAMES: Dict[str, str] = {
    "auto": "Auto-detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "el": "Greek",
    "he": "Hebrew",
    "iw": "Hebrew",
    "cs": "Czech",
    "ro": "Romanian",
    "hu": "Hungarian",
    "uk": "Ukrainian",
    "fa": "Persian",
    "sk": "Slovak",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "hr": "Croatian",
    "sr": "Serbian",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "ml": "Malayalam",
    "kn": "Kannada",
    "gu": "Gujarati",
    "ur": "Urdu",
    "ms": "Malay",
}


def whisper_to_libretranslate(whisper_code: str) -> str:
    """
    Convert Whisper language code to LibreTranslate code

    Args:
        whisper_code: Whisper language code (e.g., "en", "zh")

    Returns:
        LibreTranslate language code
    """
    return WHISPER_TO_LIBRETRANSLATE.get(whisper_code, whisper_code)


def get_language_name(code: str) -> str:
    """
    Get human-readable language name from code

    Args:
        code: Language code (e.g., "en", "es")

    Returns:
        Language name (e.g., "English", "Spanish")
    """
    return LANGUAGE_NAMES.get(code, code.upper())


def normalize_language_code(code: str) -> str:
    """
    Normalize language code to standard format

    Args:
        code: Language code in any format

    Returns:
        Normalized language code (lowercase, 2-letter)
    """
    # Convert to lowercase
    code = code.lower().strip()

    # Handle special cases
    if code in ["chinese", "mandarin"]:
        return "zh"
    elif code in ["japanese"]:
        return "ja"
    elif code in ["korean"]:
        return "ko"
    elif code in ["hebrew"]:
        return "he"

    # If it's a long code like "en-US", take first part
    if "-" in code:
        code = code.split("-")[0]
    if "_" in code:
        code = code.split("_")[0]

    # Return first 2 characters
    return code[:2]


def is_supported_language(code: str, supported_codes: list) -> bool:
    """
    Check if language code is supported

    Args:
        code: Language code to check
        supported_codes: List of supported language codes

    Returns:
        True if supported, False otherwise
    """
    normalized = normalize_language_code(code)
    return normalized in supported_codes


def get_common_languages() -> list:
    """
    Get list of most common languages for UI

    Returns:
        List of dictionaries with code and name
    """
    common = [
        "auto", "en", "es", "fr", "de", "zh", "ja", "ko",
        "ar", "hi", "pt", "ru", "it", "nl", "pl", "tr"
    ]

    return [
        {"code": code, "name": get_language_name(code)}
        for code in common
    ]


def validate_language_pair(source: str, target: str) -> tuple:
    """
    Validate and normalize language pair

    Args:
        source: Source language code
        target: Target language code

    Returns:
        Tuple of (normalized_source, normalized_target)

    Raises:
        ValueError: If language codes are invalid
    """
    # Normalize codes
    source = normalize_language_code(source) if source != "auto" else "auto"
    target = normalize_language_code(target)

    # Check if same (after normalization)
    if source == target:
        raise ValueError(f"Source and target languages are the same: {source}")

    # Check if target is auto (not allowed)
    if target == "auto":
        raise ValueError("Target language cannot be 'auto'")

    return (source, target)
