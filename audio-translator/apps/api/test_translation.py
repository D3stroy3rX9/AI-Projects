#!/usr/bin/env python3
"""
Test translation service

This script tests the translation service without needing the full API
"""
import asyncio
import sys
from services.libretranslate_service import LibreTranslateService
from services.translation_service import TranslationService


async def test_libretranslate_basic():
    """
    Test basic LibreTranslate functionality
    """
    print("=" * 60)
    print("🧪 Testing LibreTranslate Service")
    print("=" * 60)

    # Initialize LibreTranslate service
    print("\n1️⃣  Initializing LibreTranslate service...")
    try:
        service = LibreTranslateService(api_url="https://libretranslate.de")
        print("   ✅ LibreTranslate service initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False

    # Get supported languages
    print("\n2️⃣  Getting supported languages...")
    try:
        languages = await service.get_supported_languages()
        print(f"   ✅ {len(languages)} languages available")
        print(f"   Sample: {', '.join([lang['name'] for lang in languages[:5]])}")
    except Exception as e:
        print(f"   ⚠️  Failed to get languages: {e}")

    # Test translation
    print("\n3️⃣  Testing translation...")

    test_cases = [
        {"text": "Hello, how are you?", "source": "en", "target": "es", "expected": "Hola"},
        {"text": "Good morning", "source": "en", "target": "fr", "expected": "Bonjour"},
        {"text": "Thank you", "source": "en", "target": "de", "expected": "Danke"},
        {"text": "I love programming", "source": "en", "target": "ja", "expected": "プログラミング"},
    ]

    success_count = 0

    for i, test in enumerate(test_cases, 1):
        try:
            print(f"\n   Test {i}: {test['text']} ({test['source']} → {test['target']})")

            result = await service.translate(
                text=test["text"],
                source_lang=test["source"],
                target_lang=test["target"]
            )

            print(f"   ✅ Translation: {result}")
            success_count += 1

        except Exception as e:
            print(f"   ❌ Translation failed: {e}")

    print(f"\n   Success rate: {success_count}/{len(test_cases)}")

    # Close service
    await service.close()

    print("\n" + "=" * 60)
    print("✅ LibreTranslate test complete!")
    print("=" * 60)

    return success_count > 0


async def test_translation_service_with_cache():
    """
    Test translation service with caching
    """
    print("\n" + "=" * 60)
    print("🧪 Testing Translation Service with Cache")
    print("=" * 60)

    # Initialize services
    print("\n1️⃣  Initializing translation service...")
    try:
        libretranslate = LibreTranslateService(api_url="https://libretranslate.de")

        service = TranslationService(
            backend="libretranslate",
            libretranslate_service=libretranslate,
            enable_cache=True,
            cache_size=100
        )

        print("   ✅ Translation service initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False

    # Test translation with caching
    print("\n2️⃣  Testing cache functionality...")

    test_text = "Hello, this is a test message"

    try:
        # First translation (cache miss)
        print(f"\n   First translation (should be cache miss):")
        result1 = await service.translate(test_text, "en", "es")
        print(f"   Result: {result1}")

        stats1 = service.get_cache_stats()
        print(f"   Cache stats: {stats1}")

        # Second translation (cache hit)
        print(f"\n   Second translation (should be cache hit):")
        result2 = await service.translate(test_text, "en", "es")
        print(f"   Result: {result2}")

        stats2 = service.get_cache_stats()
        print(f"   Cache stats: {stats2}")

        # Verify cache working
        if stats2['hits'] > stats1['hits']:
            print("   ✅ Cache is working correctly!")
        else:
            print("   ⚠️  Cache might not be working")

        # Different translation
        print(f"\n   Different translation (should be cache miss):")
        result3 = await service.translate("Goodbye", "en", "fr")
        print(f"   Result: {result3}")

        stats3 = service.get_cache_stats()
        print(f"   Cache stats: {stats3}")

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

    # Close service
    await service.close()

    print("\n" + "=" * 60)
    print("✅ Translation service test complete!")
    print("=" * 60)

    return True


async def test_language_detection():
    """
    Test language detection
    """
    print("\n" + "=" * 60)
    print("🧪 Testing Language Detection")
    print("=" * 60)

    service = LibreTranslateService(api_url="https://libretranslate.de")

    test_texts = [
        "Hello, how are you?",
        "Bonjour, comment allez-vous?",
        "Hola, ¿cómo estás?",
        "Guten Tag, wie geht es Ihnen?",
        "こんにちは、元気ですか？",
    ]

    for text in test_texts:
        try:
            result = await service.detect_language(text)
            print(f"\n   Text: {text}")
            print(f"   Detected: {result['language']} (confidence: {result['confidence']})")
        except Exception as e:
            print(f"   ❌ Detection failed: {e}")

    await service.close()


def main():
    """
    Main test function
    """
    print("\n🌍 Translation Service Test Suite\n")

    # Check for API connectivity
    print("⚠️  Note: These tests require internet connection to access LibreTranslate API")
    print("   Public instance: https://libretranslate.de")
    print("   This is free but rate-limited\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--skip":
        print("Skipping tests (--skip flag provided)")
        return

    # Run tests
    try:
        # Test basic LibreTranslate
        asyncio.run(test_libretranslate_basic())

        # Test with caching
        asyncio.run(test_translation_service_with_cache())

        # Test language detection
        asyncio.run(test_language_detection())

    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")

    except Exception as e:
        print(f"\n\n❌ Test error: {e}")

    print("\n💡 Tips:")
    print("   - Tests use free public LibreTranslate API")
    print("   - May be slow or rate-limited during peak times")
    print("   - Consider self-hosting for production")
    print("   - Set LIBRETRANSLATE_URL in .env for custom instance")
    print()


if __name__ == "__main__":
    main()
