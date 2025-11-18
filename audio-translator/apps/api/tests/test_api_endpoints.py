"""
Tests for API REST endpoints
"""
import pytest


def test_health_check(test_client):
    """Test health check endpoint"""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "models_loaded" in data
    assert "version" in data
    assert "database" in data


def test_get_languages(test_client):
    """Test languages endpoint"""
    response = test_client.get("/languages")

    assert response.status_code == 200
    data = response.json()

    assert "languages" in data
    assert isinstance(data["languages"], list)
    assert len(data["languages"]) > 0

    # Check structure of language items
    first_lang = data["languages"][0]
    assert "code" in first_lang
    assert "name" in first_lang


def test_get_history_empty(test_client):
    """Test getting history when empty"""
    response = test_client.get("/history")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["results"] == []


def test_get_history_with_data(test_client, sample_translation):
    """Test getting history with translations"""
    response = test_client.get("/history")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert len(data["results"]) == 1

    translation = data["results"][0]
    assert translation["source_language"] == "en"
    assert translation["target_language"] == "es"
    assert translation["source_text"] == "Hello world"
    assert translation["translated_text"] == "Hola mundo"


def test_get_history_pagination(test_client, sample_translation):
    """Test history pagination"""
    response = test_client.get("/history?limit=10&offset=0")

    assert response.status_code == 200
    data = response.json()

    assert data["limit"] == 10
    assert data["offset"] == 0


def test_get_single_translation(test_client, sample_translation):
    """Test getting a single translation by ID"""
    response = test_client.get(f"/history/{sample_translation}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == sample_translation
    assert data["source_text"] == "Hello world"


def test_get_nonexistent_translation(test_client):
    """Test getting a translation that doesn't exist"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = test_client.get(f"/history/{fake_id}")

    assert response.status_code == 404


def test_delete_translation(test_client, sample_translation):
    """Test deleting a translation"""
    response = test_client.delete(f"/history/{sample_translation}")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Translation deleted successfully"
    assert data["id"] == sample_translation

    # Verify it's deleted
    get_response = test_client.get(f"/history/{sample_translation}")
    assert get_response.status_code == 404


def test_delete_nonexistent_translation(test_client):
    """Test deleting a translation that doesn't exist"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = test_client.delete(f"/history/{fake_id}")

    assert response.status_code == 404


def test_clear_all_history(test_client, sample_translation):
    """Test clearing all history"""
    response = test_client.delete("/history")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "History cleared successfully"
    assert data["deleted_count"] == 1
    assert data["session_id"] == "all"

    # Verify history is empty
    get_response = test_client.get("/history")
    assert get_response.json()["total"] == 0


def test_clear_history_by_session(test_client, sample_translation):
    """Test clearing history for specific session"""
    response = test_client.delete("/history?session_id=test-session-123")

    assert response.status_code == 200
    data = response.json()

    assert data["deleted_count"] == 1
    assert data["session_id"] == "test-session-123"


def test_websocket_connection(test_client):
    """Test WebSocket connection"""
    with test_client.websocket_connect("/ws/translate") as websocket:
        # Receive welcome message
        data = websocket.receive_json()

        assert data["type"] == "connected"
        assert "message" in data
        assert "models_loaded" in data
