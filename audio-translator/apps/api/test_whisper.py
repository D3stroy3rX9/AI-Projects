#!/usr/bin/env python3
"""
Test Whisper transcription service

This script tests the Whisper service without needing the full API
"""
import asyncio
import sys
from services.whisper_service import WhisperService
from utils.audio import convert_to_wav, clean_temp_files
import tempfile
import os


async def test_whisper_basic():
    """
    Test basic Whisper functionality
    """
    print("=" * 60)
    print("🧪 Testing Whisper Service")
    print("=" * 60)

    # Initialize Whisper service
    print("\n1️⃣  Initializing Whisper service...")
    try:
        whisper_service = WhisperService(model_name="base")
        print("   ✅ Whisper service initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        print("\n   Run: python download_models.py --model base")
        return False

    # Get model info
    print("\n2️⃣  Getting model information...")
    model_info = whisper_service.get_model_info()
    print(f"   Model: {model_info['model_name']}")
    print(f"   Loaded: {model_info['loaded']}")
    print(f"   Supported languages: {len(model_info['supported_languages'])} languages")

    # Create a simple test audio file (if you have one)
    print("\n3️⃣  Testing transcription...")
    print("   ℹ️  To test transcription, provide an audio file path")
    print("   Example: python test_whisper.py /path/to/audio.mp3")

    # If audio file provided, test it
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]

        if not os.path.exists(audio_file):
            print(f"   ❌ Audio file not found: {audio_file}")
            return False

        print(f"   Testing with: {audio_file}")

        temp_files = []

        try:
            # Convert to WAV if needed
            if not audio_file.endswith('.wav'):
                print("   🔄 Converting to WAV...")
                wav_file = convert_to_wav(audio_file)
                temp_files.append(wav_file)
            else:
                wav_file = audio_file

            # Transcribe
            print("   🎤 Transcribing audio...")
            result = await whisper_service.transcribe(wav_file)

            print(f"\n   ✅ Transcription successful!")
            print(f"   Text: {result['text']}")
            print(f"   Language: {result['language']}")
            print(f"   Confidence: {result['confidence']}")

            if result['segments']:
                print(f"   Segments: {len(result['segments'])}")

        except Exception as e:
            print(f"   ❌ Transcription failed: {e}")
            return False

        finally:
            # Cleanup
            if temp_files:
                clean_temp_files(temp_files)

    else:
        print("   ⏭️  Skipping (no audio file provided)")

    print("\n" + "=" * 60)
    print("✅ Whisper service test complete!")
    print("=" * 60)

    return True


async def test_language_detection():
    """
    Test language detection
    """
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]

        if not os.path.exists(audio_file):
            return

        print("\n" + "=" * 60)
        print("🌍 Testing Language Detection")
        print("=" * 60)

        whisper_service = WhisperService(model_name="base")

        temp_files = []

        try:
            # Convert to WAV if needed
            if not audio_file.endswith('.wav'):
                wav_file = convert_to_wav(audio_file)
                temp_files.append(wav_file)
            else:
                wav_file = audio_file

            # Detect language
            result = await whisper_service.detect_language(wav_file)

            print(f"\n✅ Language Detection:")
            print(f"   Detected: {result['language']}")
            print(f"   Confidence: {result['confidence']}")

        except Exception as e:
            print(f"❌ Language detection failed: {e}")

        finally:
            if temp_files:
                clean_temp_files(temp_files)


def main():
    """
    Main test function
    """
    print("\n🎤 Whisper Service Test Suite\n")

    # Run tests
    asyncio.run(test_whisper_basic())

    # Test language detection if audio file provided
    if len(sys.argv) > 1:
        asyncio.run(test_language_detection())

    print("\n💡 Tips:")
    print("   - Download model: python download_models.py --model base")
    print("   - Test with audio: python test_whisper.py /path/to/audio.mp3")
    print("   - Supported formats: WAV, MP3, WebM, OGG, M4A, FLAC")
    print()


if __name__ == "__main__":
    main()
