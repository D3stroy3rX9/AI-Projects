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


# Global variables for model loading
models_loaded = False
whisper_model = None
translation_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for model loading/cleanup
    """
    global models_loaded, whisper_model, translation_service

    print("🚀 Starting up Audio Auto-Translator API...")

    # Initialize database tables
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")

    # Model loading will be implemented in Prompt C & D
    print("ℹ️  Model loading will be added in Prompt C (Whisper) and D (Translation)")
    models_loaded = False

    yield

    # Cleanup on shutdown
    print("🔄 Shutting down Audio Auto-Translator API...")
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

                # For now, send placeholder response
                # Actual implementation will be in Prompt C & D
                await websocket.send_json({
                    "type": "info",
                    "message": "Audio received. Whisper transcription will be added in Prompt C."
                })

                # Placeholder transcription (will be replaced in Prompt C)
                await websocket.send_json({
                    "type": "transcription",
                    "text": "[Transcription will appear here after Prompt C]",
                    "language": source_lang if source_lang != "auto" else "en",
                    "confidence": 0.0
                })

                # Placeholder translation (will be replaced in Prompt D)
                await websocket.send_json({
                    "type": "translation",
                    "text": "[Translation will appear here after Prompt D]",
                    "source": source_lang if source_lang != "auto" else "en",
                    "target": target_lang
                })

                # Save to database (placeholder data for now)
                # In production, this will save actual transcription and translation
                try:
                    # Get database session
                    from db.database import SessionLocal
                    db = SessionLocal()

                    translation = Translation(
                        source_language=source_lang if source_lang != "auto" else "en",
                        target_language=target_lang,
                        source_text="[Placeholder - will be transcribed in Prompt C]",
                        translated_text="[Placeholder - will be translated in Prompt D]",
                        audio_duration=0.0,
                        confidence_score=0.0,
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

                except Exception as e:
                    print(f"Error saving to database: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Database error: {str(e)}"
                    })

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
