"""
Audio Auto-Translator FastAPI Backend
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List, Optional
import json
import base64
from datetime import datetime

from config import settings
from db.database import get_db, init_db, engine
from db.models import Translation
from services.whisper_service import WhisperService
from services.libretranslate_service import LibreTranslateService
from services.translation_service import TranslationService
from utils.audio import (
    save_audio_chunk,
    convert_to_wav,
    clean_temp_files,
    clean_old_temp_files,
    get_audio_duration
)
from utils.language_codes import whisper_to_libretranslate


# Global variables for model loading
models_loaded = False
whisper_service: Optional[WhisperService] = None
translation_service: Optional[TranslationService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for model loading/cleanup
    """
    global models_loaded, whisper_service, translation_service

    print("🚀 Starting up Audio Auto-Translator API...")

    # Initialize database tables
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")

    # Load Whisper model
    try:
        print(f"\n📥 Loading Whisper model: {settings.whisper_model}")
        whisper_service = WhisperService(model_name=settings.whisper_model)
        print("✅ Whisper model loaded successfully")
        models_loaded = True
    except Exception as e:
        print(f"❌ Failed to load Whisper model: {e}")
        print("   Run: python download_models.py --model base")
        models_loaded = False

    # Load Translation service
    try:
        print(f"\n📥 Loading translation service: {settings.translation_backend}")

        if settings.translation_backend == "libretranslate":
            # Initialize LibreTranslate service
            libretranslate = LibreTranslateService(api_url=settings.libretranslate_url)

            # Create translation service with LibreTranslate backend
            translation_service = TranslationService(
                backend="libretranslate",
                libretranslate_service=libretranslate,
                enable_cache=True,
                cache_size=1000
            )

            print("✅ Translation service loaded successfully")

        elif settings.translation_backend == "nllb":
            # NLLB local model (optional implementation)
            print("⚠️  NLLB backend selected but not implemented yet")
            print("   Using LibreTranslate as fallback")

            libretranslate = LibreTranslateService(api_url=settings.libretranslate_url)
            translation_service = TranslationService(
                backend="libretranslate",
                libretranslate_service=libretranslate,
                enable_cache=True
            )

        else:
            raise ValueError(f"Unknown translation backend: {settings.translation_backend}")

    except Exception as e:
        print(f"❌ Failed to load translation service: {e}")
        print("   Translation will not be available")
        translation_service = None

    # Clean old temp files on startup
    clean_old_temp_files(max_age_seconds=3600)

    yield

    # Cleanup on shutdown
    print("🔄 Shutting down Audio Auto-Translator API...")

    # Close translation service
    if translation_service:
        await translation_service.close()

    # Clean all temp files
    print("🗑️  Cleaning temporary audio files...")
    clean_old_temp_files(max_age_seconds=0)  # Delete all temp files

    # Dispose database
    engine.dispose()
    print("✅ Cleanup complete")


app = FastAPI(
    title="Audio Auto-Translator API",
    description="Real-time voice translation supporting 100+ languages",
    version="0.2.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== REST Endpoints ====================

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "models_loaded": models_loaded,
        "message": "Audio Auto-Translator API is running",
        "version": "0.2.0",
        "database": "connected" if engine else "not connected"
    }


@app.get("/languages")
async def get_languages():
    """Get supported languages"""
    # This list will be expanded in Prompt D with LibreTranslate API
    return {
        "languages": [
            {"code": "auto", "name": "Auto-detect"},
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "ar", "name": "Arabic"},
            {"code": "hi", "name": "Hindi"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "it", "name": "Italian"},
            {"code": "nl", "name": "Dutch"},
            {"code": "pl", "name": "Polish"},
            {"code": "tr", "name": "Turkish"},
            {"code": "vi", "name": "Vietnamese"},
            {"code": "th", "name": "Thai"},
            {"code": "id", "name": "Indonesian"},
            {"code": "sv", "name": "Swedish"},
            {"code": "no", "name": "Norwegian"},
        ]
    }


# ==================== History CRUD Endpoints ====================

@app.get("/history")
async def get_history(
    limit: int = 50,
    offset: int = 0,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get translation history

    Args:
        limit: Maximum number of results (default 50)
        offset: Number of results to skip (default 0)
        session_id: Filter by session ID (optional)
        db: Database session

    Returns:
        List of translations with metadata
    """
    query = db.query(Translation)

    # Filter by session_id if provided
    if session_id:
        query = query.filter(Translation.session_id == session_id)

    # Order by created_at descending (newest first)
    query = query.order_by(Translation.created_at.desc())

    # Apply pagination
    query = query.offset(offset).limit(limit)

    translations = query.all()

    return {
        "total": db.query(Translation).count(),
        "limit": limit,
        "offset": offset,
        "results": [t.to_dict() for t in translations]
    }


@app.get("/history/{translation_id}")
async def get_translation(translation_id: str, db: Session = Depends(get_db)):
    """
    Get a specific translation by ID

    Args:
        translation_id: UUID of the translation
        db: Database session

    Returns:
        Translation object
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()

    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    return translation.to_dict()


@app.delete("/history/{translation_id}")
async def delete_translation(translation_id: str, db: Session = Depends(get_db)):
    """
    Delete a specific translation by ID

    Args:
        translation_id: UUID of the translation
        db: Database session

    Returns:
        Success message
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()

    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    db.delete(translation)
    db.commit()

    return {"message": "Translation deleted successfully", "id": translation_id}


@app.delete("/history")
async def clear_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Clear translation history

    Args:
        session_id: If provided, only clear translations for this session
        db: Database session

    Returns:
        Number of translations deleted
    """
    query = db.query(Translation)

    if session_id:
        query = query.filter(Translation.session_id == session_id)

    count = query.count()
    query.delete()
    db.commit()

    return {
        "message": "History cleared successfully",
        "deleted_count": count,
        "session_id": session_id if session_id else "all"
    }


# ==================== WebSocket Endpoint ====================

@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio translation

    Client → Server message format:
    {
        "type": "audio_chunk",
        "data": "<base64-encoded-audio>",
        "source_lang": "auto" or specific like "en",
        "target_lang": "es",
        "session_id": "optional-session-id"
    }

    Server → Client message format:
    {
        "type": "transcription",
        "text": "Hello world",
        "language": "en",
        "confidence": 0.95
    }
    {
        "type": "translation",
        "text": "Hola mundo",
        "source": "en",
        "target": "es"
    }
    {
        "type": "error",
        "message": "Error description"
    }
    """
    await websocket.accept()

    try:
        print(f"✅ WebSocket client connected: {websocket.client}")

        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Audio Auto-Translator",
            "models_loaded": models_loaded
        })

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Extract message data
            msg_type = message.get("type")

            if msg_type == "audio_chunk":
                # Extract parameters
                audio_data = message.get("data")
                source_lang = message.get("source_lang", "auto")
                target_lang = message.get("target_lang", "en")
                session_id = message.get("session_id")

                # Temporary file paths for cleanup
                temp_files = []

                try:
                    # Check if Whisper is loaded
                    if whisper_service is None:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Whisper model not loaded. Run: python download_models.py --model base"
                        })
                        continue

                    # Send processing status
                    await websocket.send_json({
                        "type": "processing",
                        "message": "Processing audio..."
                    })

                    # Step 1: Save audio chunk
                    audio_file = save_audio_chunk(audio_data)
                    temp_files.append(audio_file)

                    # Step 2: Convert to WAV format for Whisper
                    wav_file = convert_to_wav(audio_file)
                    temp_files.append(wav_file)

                    # Step 3: Get audio duration
                    duration = get_audio_duration(wav_file)

                    # Step 4: Transcribe with Whisper
                    transcribe_lang = None if source_lang == "auto" else source_lang
                    result = await whisper_service.transcribe(wav_file, language=transcribe_lang)

                    # Extract transcription data
                    transcription_text = result["text"]
                    detected_language = result["language"]
                    confidence = result["confidence"]

                    # Send transcription result
                    await websocket.send_json({
                        "type": "transcription",
                        "text": transcription_text,
                        "language": detected_language,
                        "confidence": confidence,
                        "duration": duration
                    })

                    # Step 5: Translate text
                    translated_text = ""

                    if translation_service is None:
                        # Translation service not available
                        await websocket.send_json({
                            "type": "warning",
                            "message": "Translation service not available"
                        })
                        translated_text = "[Translation service not available]"

                    elif detected_language == target_lang:
                        # Same language, no translation needed
                        translated_text = transcription_text

                    else:
                        try:
                            # Convert Whisper language code to LibreTranslate code
                            source_code = whisper_to_libretranslate(detected_language)
                            target_code = whisper_to_libretranslate(target_lang)

                            # Translate
                            translated_text = await translation_service.translate(
                                text=transcription_text,
                                source_lang=source_code,
                                target_lang=target_code
                            )

                        except Exception as trans_error:
                            print(f"Translation error: {trans_error}")
                            await websocket.send_json({
                                "type": "warning",
                                "message": f"Translation failed: {str(trans_error)}"
                            })
                            translated_text = f"[Translation error: {str(trans_error)}]"

                    # Send translation result
                    await websocket.send_json({
                        "type": "translation",
                        "text": translated_text,
                        "source": detected_language,
                        "target": target_lang
                    })

                    # Save to database
                    try:
                        from db.database import SessionLocal
                        db = SessionLocal()

                        translation = Translation(
                            source_language=detected_language,
                            target_language=target_lang,
                            source_text=transcription_text,
                            translated_text=translated_text,
                            audio_duration=duration,
                            confidence_score=confidence,
                            session_id=session_id
                        )

                        db.add(translation)
                        db.commit()
                        db.refresh(translation)
                        db.close()

                        await websocket.send_json({
                            "type": "saved",
                            "translation_id": str(translation.id),
                            "message": "Translation saved to history"
                        })

                    except Exception as db_error:
                        print(f"Database error: {db_error}")
                        await websocket.send_json({
                            "type": "warning",
                            "message": f"Transcription successful but database error: {str(db_error)}"
                        })

                except Exception as e:
                    print(f"Error processing audio: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Processing error: {str(e)}"
                    })

                finally:
                    # Clean up temporary files
                    if temp_files:
                        clean_temp_files(temp_files)

            elif msg_type == "ping":
                # Respond to ping with pong
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })

    except WebSocketDisconnect:
        print(f"❌ WebSocket client disconnected: {websocket.client}")

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass


# ==================== Startup Message ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
