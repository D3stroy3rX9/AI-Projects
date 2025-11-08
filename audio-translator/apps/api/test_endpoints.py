"""
Test script to validate all API endpoints
Run this after starting the server with: uvicorn main:app --reload
"""
import requests
import json
from websockets.sync.client import connect
import time


BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    print("\n1️⃣  Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("   ✅ Health check passed")


def test_languages():
    """Test languages endpoint"""
    print("\n2️⃣  Testing languages endpoint...")
    response = requests.get(f"{BASE_URL}/languages")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Languages count: {len(data['languages'])}")
    print(f"   Sample languages: {[lang['name'] for lang in data['languages'][:5]]}")
    assert response.status_code == 200
    assert len(data['languages']) > 0
    print("   ✅ Languages endpoint passed")


def test_history_empty():
    """Test history endpoint (should be empty initially)"""
    print("\n3️⃣  Testing history endpoint (empty)...")
    response = requests.get(f"{BASE_URL}/history")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total translations: {data['total']}")
    assert response.status_code == 200
    print("   ✅ History endpoint passed")


def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n4️⃣  Testing WebSocket connection...")

    try:
        with connect(f"{WS_URL}/ws/translate") as websocket:
            # Receive welcome message
            welcome = websocket.recv()
            print(f"   Welcome message: {welcome}")

            # Send ping
            websocket.send(json.dumps({"type": "ping"}))
            pong = websocket.recv()
            print(f"   Pong response: {pong}")

            # Send test audio chunk
            test_message = {
                "type": "audio_chunk",
                "data": "dGVzdCBhdWRpbyBkYXRh",  # base64 "test audio data"
                "source_lang": "en",
                "target_lang": "es",
                "session_id": "test-session-123"
            }
            websocket.send(json.dumps(test_message))

            # Receive responses
            for i in range(4):  # info, transcription, translation, saved
                response = websocket.recv()
                data = json.loads(response)
                print(f"   Response {i+1}: {data['type']}")

            print("   ✅ WebSocket connection passed")

    except Exception as e:
        print(f"   ❌ WebSocket error: {e}")
        print("   Note: Make sure server is running with: uvicorn main:app --reload")


def test_history_after_websocket():
    """Test history endpoint after adding data"""
    print("\n5️⃣  Testing history endpoint (after data)...")
    response = requests.get(f"{BASE_URL}/history")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total translations: {data['total']}")
    if data['total'] > 0:
        print(f"   Latest translation: {data['results'][0]['id']}")
    assert response.status_code == 200
    print("   ✅ History with data passed")


def test_delete_history():
    """Test deleting history"""
    print("\n6️⃣  Testing history deletion...")

    # Get first translation ID
    response = requests.get(f"{BASE_URL}/history?limit=1")
    data = response.json()

    if data['total'] > 0:
        translation_id = data['results'][0]['id']
        print(f"   Deleting translation: {translation_id}")

        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/history/{translation_id}")
        print(f"   Status: {delete_response.status_code}")
        assert delete_response.status_code == 200
        print("   ✅ Delete endpoint passed")
    else:
        print("   ℹ️  No translations to delete")


def test_clear_all_history():
    """Test clearing all history"""
    print("\n7️⃣  Testing clear all history...")
    response = requests.delete(f"{BASE_URL}/history")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Deleted count: {data['deleted_count']}")
    assert response.status_code == 200
    print("   ✅ Clear all history passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Audio Auto-Translator API Test Suite")
    print("=" * 60)

    try:
        # REST endpoints
        test_health_check()
        test_languages()
        test_history_empty()

        # WebSocket
        test_websocket_connection()

        # History operations
        test_history_after_websocket()
        test_delete_history()
        test_clear_all_history()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print("   Make sure the server is running:")
        print("   cd apps/api && uvicorn main:app --reload")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
