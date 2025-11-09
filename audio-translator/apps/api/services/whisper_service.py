"""
Whisper speech recognition service
"""
import whisper
import asyncio
from typing import Dict, Optional, List
import os
import time


class WhisperService:
    """
    Service for speech-to-text transcription using OpenAI Whisper
    """

    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper service with specified model

        Args:
            model_name: Model size - "tiny", "base", "small", "medium", "large"
                       - tiny: 39MB, fastest, lower accuracy
                       - base: 74MB, balanced (recommended)
                       - small: 244MB, high accuracy
                       - medium: 769MB, excellent accuracy
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """
        Load Whisper model into memory

        Model is cached after first download to ~/.cache/whisper/
        """
        try:
            print(f"📥 Loading Whisper model '{self.model_name}'...")
            start_time = time.time()

            # Load model (downloads if not cached)
            self.model = whisper.load_model(self.model_name)

            load_time = time.time() - start_time
            print(f"✅ Whisper model '{self.model_name}' loaded in {load_time:.2f}s")

        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            raise

    async def transcribe(
        self,
        audio_file_path: str,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio file to text

        Args:
            audio_file_path: Path to audio file (wav, mp3, webm, etc.)
            language: Optional language code (e.g., "en", "es")
                     If None, language will be auto-detected

        Returns:
            Dictionary with:
                - text: Transcribed text
                - language: Detected/specified language code
                - confidence: Average probability score (0-1)
                - segments: List of segments with timestamps (optional)

        Raises:
            FileNotFoundError: If audio file doesn't exist
            Exception: If transcription fails
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        if self.model is None:
            raise RuntimeError("Whisper model not loaded")

        try:
            print(f"🎤 Transcribing audio: {audio_file_path}")
            start_time = time.time()

            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                audio_file_path,
                language
            )

            transcribe_time = time.time() - start_time
            print(f"✅ Transcription complete in {transcribe_time:.2f}s")

            return result

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            raise

    def _transcribe_sync(
        self,
        audio_file_path: str,
        language: Optional[str] = None
    ) -> Dict:
        """
        Synchronous transcription (runs in thread pool)
        """
        # Whisper options for CPU optimization
        options = {
            "fp16": False,  # Use FP32 on CPU (FP16 requires GPU)
            "language": language,  # None for auto-detection
            "task": "transcribe",  # "transcribe" or "translate"
            "verbose": False,  # Reduce output
        }

        # Run Whisper transcription
        result = self.model.transcribe(audio_file_path, **options)

        # Calculate average confidence from segments
        segments = result.get("segments", [])
        if segments:
            avg_confidence = sum(
                seg.get("no_speech_prob", 0.0)
                for seg in segments
            ) / len(segments)
            # Convert no_speech_prob to confidence (inverse)
            confidence = 1.0 - avg_confidence
        else:
            confidence = 0.8  # Default confidence if no segments

        # Extract relevant information
        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", language or "unknown"),
            "confidence": round(confidence, 2),
            "segments": [
                {
                    "start": seg.get("start"),
                    "end": seg.get("end"),
                    "text": seg.get("text", "").strip(),
                }
                for seg in segments
            ] if segments else []
        }

    async def detect_language(self, audio_file_path: str) -> Dict[str, float]:
        """
        Detect language from audio file

        Args:
            audio_file_path: Path to audio file

        Returns:
            Dictionary with language code and confidence
            Example: {"language": "en", "confidence": 0.95}
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        if self.model is None:
            raise RuntimeError("Whisper model not loaded")

        try:
            # Load audio and detect language
            audio = whisper.load_audio(audio_file_path)
            audio = whisper.pad_or_trim(audio)

            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

            # Detect language
            _, probs = self.model.detect_language(mel)

            # Get most likely language
            detected_language = max(probs, key=probs.get)
            confidence = probs[detected_language]

            return {
                "language": detected_language,
                "confidence": round(confidence, 2)
            }

        except Exception as e:
            print(f"❌ Language detection error: {e}")
            return {"language": "unknown", "confidence": 0.0}

    def get_model_info(self) -> Dict:
        """
        Get information about loaded model

        Returns:
            Dictionary with model name and status
        """
        return {
            "model_name": self.model_name,
            "loaded": self.model is not None,
            "supported_languages": self._get_supported_languages()
        }

    def _get_supported_languages(self) -> List[str]:
        """
        Get list of languages supported by Whisper

        Returns:
            List of language codes
        """
        # Whisper supports 99 languages
        # Full list from whisper.tokenizer.LANGUAGES
        try:
            from whisper.tokenizer import LANGUAGES
            return list(LANGUAGES.keys())
        except:
            # Fallback to common languages
            return [
                "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko",
                "ar", "hi", "nl", "pl", "tr", "vi", "th", "id", "sv", "no"
            ]


# Global instance (will be initialized in main.py lifespan)
whisper_service: Optional[WhisperService] = None


def get_whisper_service() -> WhisperService:
    """
    Get global Whisper service instance

    Returns:
        WhisperService instance

    Raises:
        RuntimeError: If service not initialized
    """
    if whisper_service is None:
        raise RuntimeError("Whisper service not initialized")
    return whisper_service
