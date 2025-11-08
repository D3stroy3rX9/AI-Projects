"""
Database models for audio translation
"""
from sqlalchemy import Column, String, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Translation(Base):
    """Translation model for storing translation history"""
    __tablename__ = "translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Language codes (e.g., "en", "es", "fr")
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)

    # Text content
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)

    # Metadata
    audio_duration = Column(Float, nullable=True)  # Duration in seconds
    confidence_score = Column(Float, nullable=True)  # Whisper confidence (0-1)

    # Optional user/session tracking
    user_id = Column(String(255), nullable=True)
    session_id = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Translation {self.source_language}→{self.target_language}: {self.source_text[:30]}...>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "source_text": self.source_text,
            "translated_text": self.translated_text,
            "audio_duration": self.audio_duration,
            "confidence_score": self.confidence_score,
            "user_id": self.user_id,
            "session_id": self.session_id,
        }
