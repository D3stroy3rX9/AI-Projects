"""
Translation service using LibreTranslate API
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional
import time
from functools import lru_cache


class LibreTranslateService:
    """
    Translation service using LibreTranslate API

    LibreTranslate is a free and open-source machine translation API
    Public instance: https://libretranslate.de (free, rate-limited)
    Self-hosted option available
    """

    def __init__(self, api_url: str = "https://libretranslate.de"):
        """
        Initialize LibreTranslate service

        Args:
            api_url: LibreTranslate API URL
        """
        self.api_url = api_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self._supported_languages: Optional[List[Dict]] = None
        print(f"🌍 LibreTranslate service initialized: {self.api_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create aiohttp session

        Returns:
            aiohttp ClientSession
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_retries: int = 3
    ) -> str:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., "en", "es")
            target_lang: Target language code (e.g., "en", "es")
            max_retries: Maximum number of retry attempts

        Returns:
            Translated text

        Raises:
            Exception: If translation fails after retries
        """
        if not text or not text.strip():
            return ""

        # If source and target are the same, return original
        if source_lang == target_lang:
            return text

        print(f"🔄 Translating: {source_lang} → {target_lang}")
        start_time = time.time()

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                session = await self._get_session()

                # LibreTranslate API endpoint
                url = f"{self.api_url}/translate"

                # Request payload
                payload = {
                    "q": text,
                    "source": source_lang,
                    "target": target_lang,
                    "format": "text"
                }

                # Make request
                async with session.post(url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        translated_text = result.get("translatedText", "")

                        elapsed = time.time() - start_time
                        print(f"✅ Translation complete in {elapsed:.2f}s")

                        return translated_text

                    elif response.status == 429:
                        # Rate limit - wait and retry
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"⚠️  Rate limited, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue

                    else:
                        error_text = await response.text()
                        raise Exception(f"API error {response.status}: {error_text}")

            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️  Timeout, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception("Translation timeout after retries")

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️  Error: {e}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception(f"Translation failed: {str(e)}")

        raise Exception("Translation failed after maximum retries")

    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages from LibreTranslate API

        Returns:
            List of dictionaries with 'code' and 'name' keys
            Example: [{"code": "en", "name": "English"}, ...]
        """
        # Return cached if available
        if self._supported_languages is not None:
            return self._supported_languages

        try:
            session = await self._get_session()

            url = f"{self.api_url}/languages"

            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    languages = await response.json()

                    # Convert to our format
                    self._supported_languages = [
                        {
                            "code": lang.get("code", ""),
                            "name": lang.get("name", "")
                        }
                        for lang in languages
                    ]

                    print(f"✅ Loaded {len(self._supported_languages)} languages from LibreTranslate")
                    return self._supported_languages

                else:
                    raise Exception(f"API error: {response.status}")

        except Exception as e:
            print(f"⚠️  Failed to get languages from API: {e}")
            # Return fallback list
            return self._get_fallback_languages()

    def _get_fallback_languages(self) -> List[Dict[str, str]]:
        """
        Get fallback language list if API is unavailable

        Returns:
            List of common languages
        """
        return [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "ar", "name": "Arabic"},
            {"code": "hi", "name": "Hindi"},
            {"code": "nl", "name": "Dutch"},
            {"code": "pl", "name": "Polish"},
            {"code": "tr", "name": "Turkish"},
            {"code": "vi", "name": "Vietnamese"},
            {"code": "th", "name": "Thai"},
            {"code": "id", "name": "Indonesian"},
            {"code": "sv", "name": "Swedish"},
            {"code": "no", "name": "Norwegian"},
        ]

    async def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect language of text (if API supports it)

        Args:
            text: Text to analyze

        Returns:
            Dictionary with detected language info
        """
        try:
            session = await self._get_session()

            url = f"{self.api_url}/detect"

            payload = {"q": text}

            async with session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()

                    # LibreTranslate returns array of detections
                    if isinstance(result, list) and len(result) > 0:
                        detection = result[0]
                        return {
                            "language": detection.get("language", "unknown"),
                            "confidence": detection.get("confidence", 0.0)
                        }

                raise Exception(f"Detection failed: {response.status}")

        except Exception as e:
            print(f"⚠️  Language detection failed: {e}")
            return {"language": "unknown", "confidence": 0.0}

    async def close(self):
        """
        Close aiohttp session
        """
        if self.session and not self.session.closed:
            await self.session.close()
            print("✅ LibreTranslate session closed")

    def __del__(self):
        """
        Cleanup on deletion
        """
        if self.session and not self.session.closed:
            # Note: This won't work in async context, but included for completeness
            try:
                asyncio.create_task(self.close())
            except:
                pass


# Global instance (will be initialized in main.py)
libretranslate_service: Optional[LibreTranslateService] = None


def get_libretranslate_service() -> LibreTranslateService:
    """
    Get global LibreTranslate service instance

    Returns:
        LibreTranslateService instance

    Raises:
        RuntimeError: If service not initialized
    """
    if libretranslate_service is None:
        raise RuntimeError("LibreTranslate service not initialized")
    return libretranslate_service
