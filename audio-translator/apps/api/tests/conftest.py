"""
Test configuration and fixtures for pytest
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.database import Base, get_db
from db.models import Translation


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def test_client():
    """Create test client with in-memory database"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Override dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    client = TestClient(app)

    yield client

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_translation(test_client):
    """Create a sample translation in the database"""
    db = TestingSessionLocal()

    translation = Translation(
        source_language="en",
        target_language="es",
        source_text="Hello world",
        translated_text="Hola mundo",
        audio_duration=2.5,
        confidence_score=0.95,
        session_id="test-session-123"
    )

    db.add(translation)
    db.commit()
    db.refresh(translation)

    translation_id = str(translation.id)

    db.close()

    return translation_id
