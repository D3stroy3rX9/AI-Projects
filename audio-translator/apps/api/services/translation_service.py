"""
Translation service with caching and multiple backend support
"""
from typing import Dict, Optional, List
import hashlib
from functools import lru_cache
import asyncio


class TranslationCache:
    """
    Simple in-memory cache for translations
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize translation cache

        Args:
            max_size: Maximum number of cached translations
        """
        self.cache: Dict[str, str] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def _make_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Generate cache key from translation parameters

        Args:
            text: Source text
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Cache key string
        """
        # Create hash of text + languages
        key_string = f"{source_lang}:{target_lang}:{text}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Get cached translation

        Args:
            text: Source text
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Cached translation or None if not found
        """
        key = self._make_key(text, source_lang, target_lang)

        if key in self.cache:
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return None

    def set(self, text: str, source_lang: str, target_lang: str, translation: str):
        """
        Store translation in cache

        Args:
            text: Source text
            source_lang: Source language code
            target_lang: Target language code
            translation: Translated text
        """
        # If cache is full, remove oldest entry (simple FIFO)
        if len(self.cache) >= self.max_size:
            # Remove first key (oldest in dict)
            first_key = next(iter(self.cache))
            del self.cache[first_key]

        key = self._make_key(text, source_lang, target_lang)
        self.cache[key] = translation

    def clear(self):
        """
        Clear all cached translations
        """
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%"
        }


class TranslationService:
    """
    Unified translation service with caching and multiple backend support
    """

    def __init__(
        self,
        backend: str = "libretranslate",
        libretranslate_service = None,
        nllb_service = None,
        enable_cache: bool = True,
        cache_size: int = 1000
    ):
        """
        Initialize translation service

        Args:
            backend: Translation backend ("libretranslate" or "nllb")
            libretranslate_service: LibreTranslateService instance
            nllb_service: NLLBService instance (optional)
            enable_cache: Enable translation caching
            cache_size: Maximum number of cached translations
        """
        self.backend = backend
        self.libretranslate_service = libretranslate_service
        self.nllb_service = nllb_service
        self.enable_cache = enable_cache

        # Initialize cache
        self.cache = TranslationCache(max_size=cache_size) if enable_cache else None

        print(f"🌍 Translation service initialized (backend: {backend}, cache: {enable_cache})")

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Translate text with caching

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Translated text

        Raises:
            Exception: If translation fails
        """
        if not text or not text.strip():
            return ""

        # If source and target are the same, return original
        if source_lang == target_lang:
            return text

        # Check cache first
        if self.cache:
            cached = self.cache.get(text, source_lang, target_lang)
            if cached is not None:
                print(f"💾 Cache hit: {source_lang} → {target_lang}")
                return cached

        # Translate using backend
        try:
            if self.backend == "libretranslate":
                if self.libretranslate_service is None:
                    raise RuntimeError("LibreTranslate service not available")

                translation = await self.libretranslate_service.translate(
                    text, source_lang, target_lang
                )

            elif self.backend == "nllb":
                if self.nllb_service is None:
                    raise RuntimeError("NLLB service not available")

                translation = await self.nllb_service.translate(
                    text, source_lang, target_lang
                )

            else:
                raise ValueError(f"Unknown backend: {self.backend}")

            # Store in cache
            if self.cache:
                self.cache.set(text, source_lang, target_lang, translation)

            return translation

        except Exception as e:
            print(f"❌ Translation error: {e}")
            raise

    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages

        Returns:
            List of language dictionaries
        """
        if self.backend == "libretranslate" and self.libretranslate_service:
            return await self.libretranslate_service.get_supported_languages()

        elif self.backend == "nllb" and self.nllb_service:
            return self.nllb_service.get_supported_languages()

        else:
            # Return fallback
            return [
                {"code": "en", "name": "English"},
                {"code": "es", "name": "Spanish"},
                {"code": "fr", "name": "French"},
                {"code": "de", "name": "German"},
            ]

    def get_cache_stats(self) -> Optional[Dict]:
        """
        Get cache statistics

        Returns:
            Cache stats or None if caching disabled
        """
        if self.cache:
            return self.cache.get_stats()
        return None

    def clear_cache(self):
        """
        Clear translation cache
        """
        if self.cache:
            self.cache.clear()
            print("✅ Translation cache cleared")

    async def close(self):
        """
        Close translation service and cleanup
        """
        if self.libretranslate_service:
            await self.libretranslate_service.close()

        if self.cache:
            stats = self.cache.get_stats()
            print(f"📊 Cache stats: {stats}")


# Global instance (will be initialized in main.py)
translation_service: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """
    Get global translation service instance

    Returns:
        TranslationService instance

    Raises:
        RuntimeError: If service not initialized
    """
    if translation_service is None:
        raise RuntimeError("Translation service not initialized")
    return translation_service
