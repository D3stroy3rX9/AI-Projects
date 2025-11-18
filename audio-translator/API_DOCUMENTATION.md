# Audio Auto-Translator - API Documentation

Complete API reference for the FastAPI backend.

---

## Base URL

**Development:** `http://localhost:8000`
**Production:** `https://your-backend-url.railway.app`

---

## Table of Contents

1. [REST Endpoints](#rest-endpoints)
2. [WebSocket Protocol](#websocket-protocol)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Authentication](#authentication)
6. [Rate Limiting](#rate-limiting)

---

## REST Endpoints

### Health Check

```http
GET /
```

Check API health and status.

**Response:**
```json
{
  "status": "ok",
  "models_loaded": true,
  "message": "Audio Auto-Translator API is running",
  "version": "0.3.0",
  "database": "connected"
}
```

---

### Get Supported Languages

```http
GET /languages
```

Retrieve list of supported languages for translation.

**Response:**
```json
{
  "languages": [
    {
      "code": "en",
      "name": "English"
    },
    {
      "code": "es",
      "name": "Spanish"
    },
    ...
  ]
}
```

---

### Get Translation History

```http
GET /history?limit=50&offset=0&session_id={session_id}
```

Retrieve translation history with pagination.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 50 | Maximum number of results |
| `offset` | integer | No | 0 | Number of results to skip |
| `session_id` | string | No | null | Filter by session ID |

**Response:**
```json
{
  "total": 100,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "id": "uuid-here",
      "created_at": "2025-01-13T12:00:00Z",
      "source_language": "en",
      "target_language": "es",
      "source_text": "Hello world",
      "translated_text": "Hola mundo",
      "audio_duration": 2.5,
      "confidence_score": 0.95,
      "user_id": null,
      "session_id": "session-123"
    },
    ...
  ]
}
```

---

### Get Single Translation

```http
GET /history/{translation_id}
```

Retrieve a specific translation by ID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `translation_id` | UUID | Yes | Translation unique identifier |

**Response:**
```json
{
  "id": "uuid-here",
  "created_at": "2025-01-13T12:00:00Z",
  "source_language": "en",
  "target_language": "es",
  "source_text": "Hello world",
  "translated_text": "Hola mundo",
  "audio_duration": 2.5,
  "confidence_score": 0.95,
  "user_id": null,
  "session_id": "session-123"
}
```

**Error Responses:**
- `404 Not Found` - Translation not found

---

### Delete Translation

```http
DELETE /history/{translation_id}
```

Delete a specific translation by ID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `translation_id` | UUID | Yes | Translation unique identifier |

**Response:**
```json
{
  "message": "Translation deleted successfully",
  "id": "uuid-here"
}
```

**Error Responses:**
- `404 Not Found` - Translation not found

---

### Clear History

```http
DELETE /history?session_id={session_id}
```

Clear all translation history, optionally filtered by session.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | No | Only clear translations for this session |

**Response:**
```json
{
  "message": "History cleared successfully",
  "deleted_count": 42,
  "session_id": "session-123"
}
```

---

## WebSocket Protocol

### Connection

```
ws://localhost:8000/ws/translate
wss://your-backend-url.railway.app/ws/translate
```

Connect to the WebSocket endpoint for real-time translation.

**Connection Flow:**

1. Client connects to WebSocket
2. Server sends `connected` message
3. Client sends `audio_chunk` message
4. Server processes and sends `transcription` → `translation` → `saved`
5. Connection remains open for multiple requests

---

### Client → Server Messages

#### Audio Chunk

Send audio data for transcription and translation.

```json
{
  "type": "audio_chunk",
  "data": "<base64-encoded-audio>",
  "source_lang": "auto",
  "target_lang": "es",
  "session_id": "session-123"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Message type, must be `"audio_chunk"` |
| `data` | string | Yes | Base64-encoded audio file (WebM, WAV, etc.) |
| `source_lang` | string | Yes | Source language code or `"auto"` for auto-detect |
| `target_lang` | string | Yes | Target language code |
| `session_id` | string | No | Session identifier for grouping translations |

#### Ping

Keep-alive message.

```json
{
  "type": "ping"
}
```

---

### Server → Client Messages

#### Connected

Sent immediately after connection.

```json
{
  "type": "connected",
  "message": "Connected to Audio Auto-Translator",
  "models_loaded": true
}
```

#### Processing

Sent when audio processing starts.

```json
{
  "type": "processing",
  "message": "Processing audio..."
}
```

#### Transcription

Sent after speech-to-text transcription completes.

```json
{
  "type": "transcription",
  "text": "Hello world",
  "language": "en",
  "confidence": 0.95,
  "duration": 2.5
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Transcribed text |
| `language` | string | Detected language code |
| `confidence` | float | Transcription confidence (0-1) |
| `duration` | float | Audio duration in seconds |

#### Translation

Sent after translation completes.

```json
{
  "type": "translation",
  "text": "Hola mundo",
  "source": "en",
  "target": "es"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Translated text |
| `source` | string | Source language code |
| `target` | string | Target language code |

#### Saved

Sent after translation is saved to database.

```json
{
  "type": "saved",
  "translation_id": "uuid-here",
  "message": "Translation saved to history"
}
```

#### Warning

Sent for non-critical issues.

```json
{
  "type": "warning",
  "message": "Translation service not available"
}
```

#### Error

Sent when an error occurs.

```json
{
  "type": "error",
  "message": "Processing error: Invalid audio format"
}
```

#### Pong

Response to ping message.

```json
{
  "type": "pong",
  "timestamp": "2025-01-13T12:00:00Z"
}
```

---

## Data Models

### Translation Model

```python
class Translation(Base):
    id: UUID                    # Primary key
    created_at: datetime        # Creation timestamp
    source_language: str        # e.g., "en"
    target_language: str        # e.g., "es"
    source_text: str            # Original transcription
    translated_text: str        # Translation result
    audio_duration: float       # Audio length in seconds
    confidence_score: float     # Whisper confidence (0-1)
    user_id: Optional[str]      # Future: user identifier
    session_id: Optional[str]   # Session grouping
```

### Language Code Mapping

Whisper uses ISO 639-1 codes, LibreTranslate may use different codes.

**Common Mappings:**

| Language | Whisper | LibreTranslate |
|----------|---------|----------------|
| English | `en` | `en` |
| Spanish | `es` | `es` |
| French | `fr` | `fr` |
| German | `de` | `de` |
| Chinese | `zh` | `zh` |
| Japanese | `ja` | `ja` |
| Hebrew | `he` | `iw` |

**Auto-detect:** Use `"auto"` for source language to let Whisper detect automatically.

---

## Error Handling

### HTTP Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### WebSocket Error Messages

All WebSocket errors are sent as messages with `type: "error"`.

**Common Errors:**

```json
{
  "type": "error",
  "message": "Whisper model not loaded. Run: python download_models.py --model base"
}
```

```json
{
  "type": "error",
  "message": "Processing error: Invalid audio format"
}
```

```json
{
  "type": "error",
  "message": "Translation failed: API rate limit exceeded"
}
```

---

## Authentication

**Current Version:** No authentication required.

**Future:** JWT-based authentication for user-specific features.

```http
Authorization: Bearer <token>
```

---

## Rate Limiting

**Current Version:** No rate limiting implemented.

**Recommended for Production:**
- **WebSocket:** 10 requests per minute per IP
- **REST API:** 100 requests per minute per IP
- **Translation:** 50 translations per hour per session

**Implementation Example:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/history")
@limiter.limit("100/minute")
async def get_history():
    pass
```

---

## CORS Configuration

The API allows cross-origin requests from configured origins.

**Configuration:**

```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Environment Variable:**

```env
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

---

## WebSocket Connection Examples

### JavaScript/TypeScript

```typescript
const ws = new WebSocket('ws://localhost:8000/ws/translate');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'transcription') {
    console.log('Transcription:', data.text);
  } else if (data.type === 'translation') {
    console.log('Translation:', data.text);
  }
};

// Send audio
const audioBlob = ...;  // Your audio blob
const reader = new FileReader();

reader.onloadend = () => {
  const base64 = reader.result.split(',')[1];

  ws.send(JSON.stringify({
    type: 'audio_chunk',
    data: base64,
    source_lang: 'auto',
    target_lang: 'es',
    session_id: 'my-session'
  }));
};

reader.readAsDataURL(audioBlob);
```

### Python

```python
import websockets
import json
import base64
import asyncio

async def translate_audio(audio_file_path):
    uri = "ws://localhost:8000/ws/translate"

    async with websockets.connect(uri) as websocket:
        # Read audio file
        with open(audio_file_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode()

        # Send audio
        message = {
            'type': 'audio_chunk',
            'data': audio_data,
            'source_lang': 'auto',
            'target_lang': 'es',
            'session_id': 'my-session'
        }

        await websocket.send(json.dumps(message))

        # Receive messages
        async for message in websocket:
            data = json.loads(message)

            if data['type'] == 'transcription':
                print(f"Transcription: {data['text']}")

            elif data['type'] == 'translation':
                print(f"Translation: {data['text']}")
                break

asyncio.run(translate_audio('test.wav'))
```

---

## Testing the API

### cURL Examples

**Health Check:**
```bash
curl http://localhost:8000/
```

**Get Languages:**
```bash
curl http://localhost:8000/languages
```

**Get History:**
```bash
curl http://localhost:8000/history?limit=10
```

**Delete Translation:**
```bash
curl -X DELETE http://localhost:8000/history/{uuid}
```

### WebSocket Testing

Use a WebSocket client tool:
- **Postman** (supports WebSocket)
- **wscat:** `npm install -g wscat`
- **websocat:** https://github.com/vi/websocat

**Example with wscat:**

```bash
wscat -c ws://localhost:8000/ws/translate
```

---

## Performance Considerations

### Request Timeouts

- **Transcription:** ~2-10 seconds (depends on audio length and model)
- **Translation:** ~1-3 seconds (depends on text length and API)
- **Total:** ~3-13 seconds per request

### Concurrent Connections

- **WebSocket:** Supports multiple concurrent connections
- **Database:** Connection pool of 5-20 connections
- **Whisper:** Single model instance shared across requests

### Optimization Tips

1. **Cache Translations:**
   - Already implemented in `TranslationService`
   - Reduces API calls by ~80%

2. **Use Smaller Whisper Model:**
   - `tiny`: 39MB, fastest, 80% accuracy
   - `base`: 74MB, balanced, 90% accuracy
   - `small`: 244MB, slower, 95% accuracy

3. **Limit Audio Duration:**
   - Recommend max 60 seconds per recording
   - Longer audio = longer processing time

---

## Summary

The Audio Auto-Translator API provides:

- ✅ RESTful endpoints for history management
- ✅ WebSocket protocol for real-time translation
- ✅ Automatic language detection via Whisper
- ✅ Translation via LibreTranslate API
- ✅ Session-based history grouping
- ✅ CORS support for web clients

**Base URL:** `http://localhost:8000` (development)

**WebSocket:** `ws://localhost:8000/ws/translate`

**Documentation:** OpenAPI/Swagger at `http://localhost:8000/docs`

Happy integrating! 🚀
