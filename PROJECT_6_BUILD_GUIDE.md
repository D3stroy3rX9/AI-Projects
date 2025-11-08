# Project 6: Audio Auto-Translator - Build Guide

**8 Claude Code Prompts to Build a Real-Time Voice Translation System**

Follow these prompts in order (a → h) to build a production-ready audio translation application using Whisper + NLLB/LibreTranslate.

---

## Prerequisites

- **Python 3.11+** installed
- **Node.js 18+** and **pnpm** installed
- **Docker** (optional, for PostgreSQL)
- **Microphone** access in browser
- **8GB+ RAM** recommended (for models)

---

## Architecture Overview

```
User speaks → Browser → WebSocket → FastAPI Backend
                                    ↓
                            Whisper (transcribe)
                                    ↓
                            NLLB/LibreTranslate (translate)
                                    ↓
                            PostgreSQL (save)
                                    ↓
                        Stream back → Display + TTS
```

---

# Prompt A: Project Scaffold & Dependencies

**Goal:** Set up monorepo structure, install dependencies, configure Docker for PostgreSQL

```
Create a real-time audio translation application with the following structure:

PROJECT STRUCTURE:
audio-translator/
├── apps/
│   ├── web/           # Next.js 14 frontend
│   └── api/           # Python FastAPI backend
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md

FRONTEND (apps/web):
- Next.js 14 with TypeScript and App Router
- TailwindCSS for styling
- Dependencies:
  - WebSocket client (native browser)
  - Recharts or Chart.js for audio visualization
  - lucide-react for icons

BACKEND (apps/api):
- Python FastAPI with async support
- Dependencies in requirements.txt:
  - fastapi>=0.109.0
  - uvicorn[standard]>=0.27.0
  - python-multipart  # File uploads
  - websockets>=12.0
  - openai-whisper    # Speech recognition
  - torch             # PyTorch for Whisper
  - transformers      # For NLLB translation
  - sentencepiece     # Required for NLLB
  - pydantic>=2.0
  - pydantic-settings
  - python-dotenv
  - sqlalchemy>=2.0
  - psycopg2-binary   # PostgreSQL driver
  - alembic           # Migrations

DOCKER COMPOSE:
- PostgreSQL 16 (port 5432)
- Volumes for postgres data persistence

ENVIRONMENT VARIABLES (.env.example):
- DATABASE_URL=postgresql://user:password@localhost:5432/audio_translator
- WHISPER_MODEL=base  # Options: tiny, base, small, medium
- TRANSLATION_BACKEND=libretranslate  # or "nllb"
- LIBRETRANSLATE_URL=https://libretranslate.de  # Free public instance
- CORS_ORIGINS=http://localhost:3000

GITIGNORE:
- Python: __pycache__, *.pyc, venv/, .env
- Node: node_modules/, .next/, .env.local
- Models: apps/api/models/*.pt (large model files)
- IDE: .vscode/, .idea/

README:
- Project overview
- Quick start instructions
- Tech stack list
- Model download instructions

Initialize both package.json (web) and requirements.txt (api) with proper dependencies.
```

**Validation:**
- [ ] Can run `pnpm install` in apps/web
- [ ] Can run `pip install -r requirements.txt` in apps/api
- [ ] `docker-compose up -d` starts PostgreSQL
- [ ] .env file created from .env.example

---

# Prompt B: Database Models & Core Backend Setup

**Goal:** Set up database models, FastAPI app structure, WebSocket endpoint

```
Set up the FastAPI backend with database models and WebSocket support:

DATABASE MODELS (apps/api/db/models.py):

1. Translation table:
   - id (UUID, primary key)
   - created_at (timestamp with timezone)
   - source_language (string, 10 chars) - e.g., "en", "es"
   - target_language (string, 10 chars)
   - source_text (text) - original transcription
   - translated_text (text) - translation result
   - audio_duration (float) - seconds
   - confidence_score (float, 0-1) - Whisper confidence
   - user_id (string, nullable) - for future user support
   - session_id (string) - group related translations

2. Create SQLAlchemy Base and Session setup in db/database.py

FASTAPI APP (apps/api/main.py):

1. Create FastAPI app with:
   - CORS middleware (allow localhost:3000)
   - Lifespan context manager for model loading
   - Error handling middleware

2. Endpoints:
   - GET / - Health check, return {"status": "ok", "models_loaded": true/false}
   - GET /languages - Return list of supported languages
   - GET /history - Get recent translations (limit 50)
   - DELETE /history/{id} - Delete translation by ID

3. WebSocket endpoint: /ws/translate
   - Accept audio chunks from client
   - Process with Whisper (transcribe)
   - Translate using LibreTranslate API
   - Stream results back to client
   - Save to database

WebSocket message format (JSON):
Client → Server:
{
  "type": "audio_chunk",
  "data": "<base64-encoded-audio>",
  "source_lang": "auto",  # or specific like "en"
  "target_lang": "es"
}

Server → Client:
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
  "message": "Translation failed"
}

CONFIGURATION (apps/api/config.py):
- Use pydantic-settings for environment variables
- Settings: DATABASE_URL, WHISPER_MODEL, TRANSLATION_BACKEND, CORS_ORIGINS

Create Alembic migration for initial schema.
```

**Validation:**
- [ ] `uvicorn main:app --reload` starts successfully
- [ ] GET http://localhost:8000/ returns health check
- [ ] GET http://localhost:8000/languages returns language list
- [ ] WebSocket connects at ws://localhost:8000/ws/translate
- [ ] Database tables created successfully

---

# Prompt C: Whisper Integration & Audio Processing

**Goal:** Integrate OpenAI Whisper for speech-to-text transcription

```
Implement Whisper speech recognition service:

WHISPER SERVICE (apps/api/services/whisper_service.py):

Create WhisperService class:

1. __init__(model_name="base"):
   - Load Whisper model on initialization
   - Cache model in memory (don't reload per request)
   - Handle model download if not present
   - Support models: tiny, base, small, medium

2. async transcribe(audio_file_path, language="auto"):
   - Transcribe audio file using Whisper
   - Return dict with:
     {
       "text": str,
       "language": str,  # detected or specified
       "confidence": float,
       "segments": list  # word-level timestamps (optional)
     }
   - Handle errors gracefully (corrupted audio, etc.)

3. detect_language(audio_file_path):
   - Use Whisper's language detection
   - Return language code and confidence

AUDIO UTILS (apps/api/utils/audio.py):

1. save_audio_chunk(base64_data, output_path):
   - Decode base64 audio from WebSocket
   - Save as temporary .wav or .webm file
   - Return file path

2. convert_to_wav(input_path):
   - Convert WebM/other formats to WAV (16kHz, mono)
   - Use ffmpeg via subprocess or pydub
   - Return converted file path

3. clean_temp_files(file_paths):
   - Delete temporary audio files after processing
   - Prevent disk space issues

UPDATE WEBSOCKET HANDLER (apps/api/main.py):

In /ws/translate WebSocket:
1. Receive audio chunk from client
2. Save to temp file using save_audio_chunk()
3. Convert to WAV format
4. Call whisper_service.transcribe()
5. Send transcription result to client
6. Clean up temp files

MODEL DOWNLOAD SCRIPT (apps/api/download_models.py):

Create script to pre-download Whisper model:
- Check if model exists in cache (~/.cache/whisper/)
- If not, download using whisper.load_model()
- Print download progress
- Verify model loads successfully

Usage: python download_models.py --model base

PERFORMANCE OPTIMIZATION:
- Run Whisper on CPU (no GPU required for base model)
- Use fp16=False for CPU inference
- Set num_workers=1 to avoid threading issues
- Implement timeout (30 seconds max for transcription)
```

**Validation:**
- [ ] `python download_models.py --model base` downloads Whisper
- [ ] Can transcribe a test audio file
- [ ] WebSocket receives audio, returns transcription
- [ ] Detected language is correct for non-English audio
- [ ] Temp files are cleaned up after processing

---

# Prompt D: Translation Service Integration

**Goal:** Add translation using LibreTranslate API (or optionally NLLB local model)

```
Implement translation service with LibreTranslate API:

TRANSLATION SERVICE (apps/api/services/translation_service.py):

Create TranslationService class with two backends:

1. LibreTranslate Backend (default, easier):

   class LibreTranslateService:
       def __init__(self, api_url="https://libretranslate.de"):
           - Set API URL from config
           - Create aiohttp session for async requests

       async def translate(text, source_lang, target_lang):
           - POST to {api_url}/translate
           - Payload: {"q": text, "source": source_lang, "target": target_lang}
           - Return translated text
           - Handle errors (rate limits, API down, etc.)
           - Add retry logic (3 attempts with exponential backoff)

       async def get_supported_languages():
           - GET {api_url}/languages
           - Return list of {code, name} pairs
           - Cache for 24 hours (languages don't change often)

2. NLLB Backend (optional, local model):

   class NLLBService:
       def __init__(self, model_name="facebook/nllb-200-distilled-600M"):
           - Load NLLB model and tokenizer from HuggingFace
           - Cache in memory
           - Map language codes (e.g., "en" → "eng_Latn")

       async def translate(text, source_lang, target_lang):
           - Use transformers pipeline for translation
           - Run inference on CPU
           - Return translated text
           - Set max_length=400 to handle long texts

       def get_supported_languages():
           - Return NLLB's 200 language codes
           - Map to human-readable names

LANGUAGE MAPPING (apps/api/utils/language_codes.py):

Create mapping of common language codes to names:
{
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ar": "Arabic",
    "hi": "Hindi",
    "pt": "Portuguese",
    "ru": "Russian",
    # ... add top 50 languages
}

Also map Whisper language codes to LibreTranslate codes if different.

UPDATE WEBSOCKET HANDLER (apps/api/main.py):

After transcription:
1. Get translated text from translation_service.translate()
2. Send translation message to client
3. Save both transcription and translation to database

CACHING (optional but recommended):

Implement simple translation cache:
- Key: hash(source_text + source_lang + target_lang)
- Value: translated text
- Store in Redis or in-memory dict (lru_cache)
- TTL: 24 hours
- Saves API calls and reduces latency

ERROR HANDLING:

- If LibreTranslate API fails, return graceful error
- If offline, suggest user to install NLLB model
- Log all translation errors for debugging
```

**Validation:**
- [ ] Can translate "Hello" from en → es using LibreTranslate API
- [ ] GET /languages returns list of supported languages
- [ ] WebSocket flow: audio → transcription → translation works end-to-end
- [ ] Translation cache prevents duplicate API calls
- [ ] Errors are handled gracefully (API down, rate limit)

---

# Prompt E: Frontend - Audio Recording & WebSocket

**Goal:** Build Next.js frontend with audio recording and real-time display

```
Create the frontend audio recording interface with WebSocket connection:

MAIN PAGE (apps/web/app/page.tsx):

1. Layout:
   - Header with app title and language selectors
   - Center: Audio recorder component
   - Bottom: Translation display area
   - Right sidebar: Recent history (optional)

2. State management:
   - sourceLanguage (default: "auto")
   - targetLanguage (default: "es")
   - isRecording (boolean)
   - transcription (string)
   - translation (string)
   - isProcessing (boolean)

AUDIO RECORDER COMPONENT (apps/web/components/AudioRecorder.tsx):

1. Features:
   - Record button (Click to start/stop)
   - Visual indicator when recording (red dot, pulsing animation)
   - Audio waveform visualization (optional: use canvas or library)
   - Recording timer (show duration)
   - Audio level meter (show mic input level)

2. Implementation:
   - Use MediaRecorder API to capture audio
   - Request microphone permission
   - Capture as WebM or WAV format
   - On stop: convert to base64, send via WebSocket
   - Handle errors (mic denied, not supported browser)

3. Code structure:
   ```typescript
   const AudioRecorder = ({ onAudioRecorded }) => {
     const [isRecording, setIsRecording] = useState(false);
     const mediaRecorderRef = useRef<MediaRecorder | null>(null);
     const chunksRef = useRef<Blob[]>([]);

     const startRecording = async () => {
       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
       const mediaRecorder = new MediaRecorder(stream);

       mediaRecorder.ondataavailable = (e) => {
         chunksRef.current.push(e.data);
       };

       mediaRecorder.onstop = () => {
         const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
         const reader = new FileReader();
         reader.onloadend = () => {
           const base64 = reader.result.split(',')[1];
           onAudioRecorded(base64);
         };
         reader.readAsDataURL(blob);
         chunksRef.current = [];
       };

       mediaRecorder.start();
       mediaRecorderRef.current = mediaRecorder;
       setIsRecording(true);
     };

     const stopRecording = () => {
       mediaRecorderRef.current?.stop();
       setIsRecording(false);
     };

     return (
       <button onClick={isRecording ? stopRecording : startRecording}>
         {isRecording ? 'Stop' : 'Record'}
       </button>
     );
   };
   ```

WEBSOCKET HOOK (apps/web/hooks/useWebSocket.ts):

1. Custom hook for WebSocket connection:
   - Connect to ws://localhost:8000/ws/translate
   - Send audio chunks with source/target languages
   - Receive transcription and translation events
   - Handle reconnection on disconnect
   - Expose: { send, messages, isConnected }

2. Message handling:
   - On "transcription" message: update UI with original text
   - On "translation" message: update UI with translated text
   - On "error" message: show error toast/notification

LANGUAGE SELECTOR (apps/web/components/LanguageSelector.tsx):

1. Dropdown select for source language:
   - Option: "Auto-detect" (default)
   - List of common languages
   - Search/filter capability

2. Dropdown select for target language:
   - List of supported languages
   - Remember last selection (localStorage)

3. Swap button (↔️) to switch source ↔ target

TRANSLATION DISPLAY (apps/web/components/TranslationDisplay.tsx):

1. Two-column layout:
   - Left: Original transcription (with detected language flag)
   - Right: Translation (with target language flag)

2. Features:
   - Copy button for each text
   - Text-to-speech playback button (use Web Speech API)
   - Confidence score display
   - Loading skeleton while processing

STYLING:
- Use TailwindCSS
- Responsive design (mobile-friendly)
- Smooth transitions and animations
- Accessibility: keyboard navigation, ARIA labels
```

**Validation:**
- [ ] Can click record button and capture audio
- [ ] Recording indicator shows when active
- [ ] Audio is sent to backend via WebSocket
- [ ] Transcription appears in UI within 10 seconds
- [ ] Translation appears below transcription
- [ ] Language selectors work correctly
- [ ] UI is responsive on mobile

---

# Prompt F: Text-to-Speech & History

**Goal:** Add TTS playback and conversation history features

```
Implement text-to-speech and conversation history:

TEXT-TO-SPEECH (apps/web/components/TTSPlayer.tsx):

1. Use Browser Web Speech API:
   ```typescript
   const speakText = (text: string, language: string) => {
     const utterance = new SpeechSynthesisUtterance(text);
     utterance.lang = language; // e.g., 'es-ES' for Spanish
     utterance.rate = 1.0; // Adjustable speed
     speechSynthesis.speak(utterance);
   };
   ```

2. Features:
   - Speaker icon button next to each translation
   - Play/pause control
   - Speed adjustment (0.5x, 1x, 1.5x, 2x)
   - Voice selection (if multiple voices available)
   - Visual indicator when speaking (animated icon)

3. TTS Controls Panel:
   - Volume slider
   - Pitch adjustment
   - Auto-play toggle (automatically speak translations)

BACKEND TTS SERVICE (optional, apps/api/services/tts_service.py):

Alternative to browser TTS for better quality:

1. Use gTTS (Google Text-to-Speech) library:
   ```python
   from gtts import gTTS
   import tempfile

   async def text_to_speech(text: str, language: str):
       tts = gTTS(text=text, lang=language)
       temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
       tts.save(temp_file.name)
       return temp_file.name  # Return audio file path
   ```

2. API endpoint: GET /tts?text=...&lang=...
   - Generate audio file
   - Return as streaming response
   - Cache generated audio files

HISTORY PAGE (apps/web/app/history/page.tsx):

1. Fetch translations from GET /history endpoint
2. Display in reverse chronological order (newest first)
3. Table/list view with columns:
   - Timestamp
   - Source language → Target language
   - Original text (truncated)
   - Translation (truncated)
   - Actions: View full, Copy, Delete, Replay

4. Features:
   - Search/filter by language or text
   - Pagination (20 items per page)
   - Delete individual translations
   - Clear all history button
   - Export as JSON or CSV

HISTORY COMPONENT (apps/web/components/TranslationHistory.tsx):

1. Collapsible sidebar on main page showing recent 5 translations
2. Click to expand full text
3. Click item to load into main display
4. Auto-refresh when new translation added

BACKEND HISTORY ENDPOINTS (apps/api/main.py):

1. GET /history?limit=50&offset=0&session_id=...
   - Return paginated translations
   - Filter by session_id if provided
   - Order by created_at DESC

2. DELETE /history/{id}
   - Soft delete or hard delete translation
   - Return 204 No Content on success

3. DELETE /history
   - Clear all history (with confirmation)
   - Optional: only clear current session

STORAGE & SESSIONS:

1. Generate session_id on page load (UUID)
2. Store in sessionStorage
3. Group related translations by session_id
4. Show session-based history grouping

EXPORT FEATURE (apps/web/components/ExportHistory.tsx):

1. Export as JSON:
   - Download all translations as JSON file
   - Include timestamps, languages, texts

2. Export as CSV:
   - Format: timestamp, source_lang, target_lang, source_text, translated_text
   - Excel-compatible

3. Export as TXT:
   - Human-readable conversation format
   - Include timestamps and language indicators
```

**Validation:**
- [ ] Can click speaker icon to hear translation
- [ ] TTS speaks in correct language
- [ ] History page shows all past translations
- [ ] Can delete individual history items
- [ ] Export to JSON/CSV works correctly
- [ ] Session-based grouping works

---

# Prompt G: Conversation Mode & UI Polish

**Goal:** Add two-way conversation mode and polish the user experience

```
Implement conversation mode and UI enhancements:

CONVERSATION MODE (apps/web/app/conversation/page.tsx):

1. Layout:
   - Split screen: Person A (left) | Person B (right)
   - Each side has:
     - Language selector
     - Record button
     - Conversation history (scrollable)
   - Messages color-coded by speaker

2. Workflow:
   - Person A speaks in Language X
   - Translation shown on Person B's side in Language Y
   - Person B speaks in Language Y
   - Translation shown on Person A's side in Language X
   - Alternating turns, automatic language detection

3. Features:
   - Auto-scroll to latest message
   - Timestamp for each message
   - Speaker labels ("You" and "Other")
   - Export full conversation
   - Clear conversation button

CONVERSATION COMPONENT (apps/web/components/ConversationView.tsx):

1. Message bubble design:
   - Left-aligned for Person A (blue)
   - Right-aligned for Person B (green)
   - Show original text (small, gray)
   - Show translation (large, black)
   - Timestamp below

2. State management:
   - messages array: { id, speaker, sourceText, translatedText, timestamp }
   - currentSpeaker: 'A' | 'B'
   - Auto-switch speaker after each translation

UI IMPROVEMENTS:

1. Loading States:
   - Skeleton loader while processing audio
   - Pulsing animation during transcription
   - Progress bar for translation
   - Estimated time remaining (based on audio duration)

2. Error Handling:
   - Toast notifications for errors
   - Retry button if transcription/translation fails
   - Fallback UI if microphone not available
   - Graceful degradation if WebSocket disconnects

3. Animations:
   - Smooth fade-in for new translations
   - Slide-up for conversation messages
   - Pulse effect on recording button
   - Waveform animation while recording

4. Accessibility:
   - Keyboard shortcuts:
     - Space: Start/stop recording
     - Ctrl+Enter: Play TTS
     - Ctrl+C: Copy translation
   - Screen reader support (ARIA labels)
   - High contrast mode support
   - Focus indicators

SETTINGS PAGE (apps/web/app/settings/page.tsx):

1. User preferences:
   - Default source/target languages
   - Auto-detect language toggle
   - Auto-play TTS toggle
   - TTS voice selection
   - TTS speed default
   - Theme (light/dark mode)
   - Audio quality (sample rate)

2. Model settings (advanced):
   - Whisper model size (tiny/base/small)
   - Translation backend (LibreTranslate/NLLB)
   - Cache enabled/disabled

3. Privacy settings:
   - Save history toggle
   - Auto-delete after X days
   - Clear cache button

THEME SUPPORT (apps/web/app/layout.tsx):

1. Implement dark mode:
   - Use next-themes package
   - Toggle in header
   - Persist preference in localStorage
   - TailwindCSS dark: classes

PERFORMANCE OPTIMIZATIONS:

1. Frontend:
   - Debounce WebSocket messages
   - Lazy load history (virtual scrolling for long lists)
   - Optimize re-renders (useMemo, useCallback)
   - Code splitting (dynamic imports)

2. Backend:
   - Cache Whisper model in memory (don't reload)
   - Connection pooling for database
   - Rate limiting to prevent abuse
   - Compress WebSocket messages

MOBILE RESPONSIVENESS:

1. Optimize for mobile:
   - Touch-friendly buttons (min 44px tap target)
   - Simplified layout on small screens
   - Bottom navigation for mobile
   - Install prompt for PWA (Progressive Web App)

2. PWA Setup:
   - Create manifest.json
   - Service worker for offline support
   - Add to home screen capability
   - Cache static assets
```

**Validation:**
- [ ] Conversation mode allows two-way translation
- [ ] Messages display correctly in conversation view
- [ ] Dark mode toggle works
- [ ] Settings persist across sessions
- [ ] Keyboard shortcuts function correctly
- [ ] Mobile layout is usable
- [ ] Loading states show during processing
- [ ] Error messages display appropriately

---

# Prompt H: Testing, Documentation & Deployment

**Goal:** Add tests, comprehensive documentation, and deployment configuration

```
Add testing, documentation, and prepare for deployment:

BACKEND TESTS (apps/api/tests/):

1. test_whisper_service.py:
   - Test transcription with sample audio file
   - Test language detection
   - Test error handling (invalid audio)
   - Test model loading/caching

2. test_translation_service.py:
   - Test LibreTranslate API calls
   - Test language code mapping
   - Test caching mechanism
   - Mock API responses

3. test_api_endpoints.py:
   - Test health check endpoint
   - Test /languages endpoint
   - Test /history CRUD operations
   - Test WebSocket connection
   - Integration test: audio → transcription → translation

4. test_database.py:
   - Test model creation
   - Test queries (pagination, filtering)
   - Test cascading deletes

Setup pytest with fixtures:
- Sample audio files in tests/fixtures/
- Mock translation responses
- In-memory database for tests

Run with: pytest tests/ -v --cov=.

FRONTEND TESTS (apps/web/__tests__/):

1. AudioRecorder.test.tsx:
   - Test microphone permission request
   - Test recording start/stop
   - Test audio data conversion

2. WebSocket.test.ts:
   - Test connection/disconnection
   - Test message sending/receiving
   - Test reconnection logic

3. TranslationDisplay.test.tsx:
   - Test rendering transcription/translation
   - Test copy functionality
   - Test TTS playback

Use Jest + React Testing Library.

Run with: pnpm test

DOCUMENTATION:

1. README.md (root):
   ```markdown
   # Audio Auto-Translator

   Real-time voice translation supporting 100+ languages using Whisper + LibreTranslate.

   ## Features
   - 🎤 Voice recording with auto language detection
   - 🌍 100+ language translation
   - 🔊 Text-to-speech playback
   - 💬 Conversation mode (two-way)
   - 📝 History with export
   - 🔒 Privacy-first (local processing)
   - 💰 100% free (no API keys required)

   ## Quick Start

   ### Prerequisites
   - Python 3.11+
   - Node.js 18+
   - Docker (optional)

   ### Installation
   1. Clone repo
   2. Start database: `docker-compose up -d`
   3. Backend setup:
      ```bash
      cd apps/api
      pip install -r requirements.txt
      python download_models.py --model base
      uvicorn main:app --reload
      ```
   4. Frontend setup:
      ```bash
      cd apps/web
      pnpm install
      pnpm dev
      ```
   5. Open http://localhost:3000

   ## Usage
   1. Click "Record" button
   2. Speak in any language
   3. See transcription + translation
   4. Click speaker icon to hear translation

   ## Tech Stack
   - Frontend: Next.js 14, TypeScript, TailwindCSS
   - Backend: FastAPI, Python
   - ML: Whisper (speech), LibreTranslate (translation)
   - Database: PostgreSQL

   ## License
   MIT (code) + Model licenses (Whisper: MIT, NLLB: CC-BY-NC)
   ```

2. API_DOCUMENTATION.md:
   - Document all REST endpoints
   - Document WebSocket protocol
   - Request/response examples
   - Error codes and meanings

3. DEPLOYMENT.md:
   - Railway deployment guide
   - Vercel deployment guide
   - Environment variable configuration
   - Domain setup
   - SSL certificate

DEPLOYMENT CONFIGURATION:

1. Dockerfile (apps/api/Dockerfile):
   ```dockerfile
   FROM python:3.11-slim

   # Install ffmpeg for audio processing
   RUN apt-get update && apt-get install -y ffmpeg

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Download Whisper model during build
   RUN python -c "import whisper; whisper.load_model('base')"

   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Railway/Render config:
   - Set Python version
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment variables from .env

3. Vercel config (apps/web/vercel.json):
   ```json
   {
     "buildCommand": "pnpm build",
     "outputDirectory": ".next",
     "env": {
       "NEXT_PUBLIC_WS_URL": "@ws_url"
     }
   }
   ```

PRODUCTION OPTIMIZATIONS:

1. Backend:
   - Enable production logging
   - Use connection pooling (10-20 connections)
   - Set request timeouts (30 seconds)
   - Enable GZIP compression
   - Add rate limiting (10 requests/min per IP)

2. Frontend:
   - Enable production build optimizations
   - Minimize bundle size (code splitting)
   - Enable SWR for caching
   - Service worker for offline support

MONITORING & OBSERVABILITY:

1. Add logging:
   - Structured logging with Python logging module
   - Log all transcriptions (privacy: hash audio)
   - Log translation requests (track usage)
   - Error tracking (Sentry integration optional)

2. Metrics:
   - Track transcription latency
   - Track translation latency
   - Count requests per language pair
   - Monitor model memory usage

3. Health checks:
   - Endpoint for model availability
   - Database connection check
   - Disk space check (for temp files)

FINAL POLISH:

1. Add landing page:
   - Hero section with demo video/GIF
   - Feature showcase
   - Supported languages list
   - Getting started guide

2. Add analytics (optional):
   - Privacy-respecting analytics (Plausible/Umami)
   - Track popular language pairs
   - Track feature usage

3. Add feedback mechanism:
   - Report translation quality issues
   - Suggest new features
   - Bug reporting

DEPLOYMENT CHECKLIST:

- [ ] All tests passing (backend + frontend)
- [ ] Environment variables configured
- [ ] Database migrations run successfully
- [ ] Models downloaded and cached
- [ ] CORS configured correctly
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Error monitoring setup
- [ ] Backup strategy for database
- [ ] Documentation complete
```

**Validation:**
- [ ] All backend tests pass (pytest)
- [ ] All frontend tests pass (pnpm test)
- [ ] README has clear setup instructions
- [ ] Can deploy to Railway/Render successfully
- [ ] Can deploy frontend to Vercel successfully
- [ ] WebSocket works in production (wss://)
- [ ] Models load correctly in production
- [ ] End-to-end flow works in production

---

## Post-Deployment Checklist

- [ ] Test on mobile devices (iOS Safari, Android Chrome)
- [ ] Test microphone permission flow
- [ ] Test with various languages
- [ ] Test conversation mode
- [ ] Monitor error rates in first 24 hours
- [ ] Check database storage growth
- [ ] Verify temp files are cleaned up
- [ ] Test offline mode (if PWA enabled)

---

## Future Enhancements

**Phase 2:**
- Streaming transcription (show words as spoken)
- Multi-speaker detection
- Accent/dialect selection
- Video file translation support

**Phase 3:**
- User accounts and authentication
- Shared translation memory
- Custom vocabulary (medical, legal terms)
- API for developers

**Phase 4:**
- Mobile apps (React Native)
- Browser extension
- Slack/Discord bot integration
- Enterprise features (team collaboration)

---

## Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Documentation:** See docs/ folder
- **Community:** Discord (optional)

---

## Cost Breakdown

**Development (Free):**
- Whisper: Free, open-source
- LibreTranslate: Free public API
- PostgreSQL: Free (Docker local)
- Next.js: Free
- FastAPI: Free

**Production (Free Tier):**
- Backend: Railway ($5/month credit, sufficient)
- Frontend: Vercel (unlimited free)
- Database: Neon/Supabase (500MB free)
- Total: $0-5/month

**Alternative (Fully Free):**
- Backend: Render (750 hours free)
- Frontend: Vercel (unlimited)
- Database: Render PostgreSQL (90 days free)
- Total: $0/month

---

## Timeline

- **Prompt A-D:** 4 hours (backend core)
- **Prompt E-F:** 3 hours (frontend + features)
- **Prompt G:** 2 hours (conversation mode + polish)
- **Prompt H:** 1 hour (testing + deployment)
- **Total:** 6-8 hours

---

**You've now built a production-ready audio translation app!** 🎉

Test it thoroughly, deploy to production, and add it to your portfolio. This project demonstrates:
- ML model integration (Whisper, NLLB)
- Real-time systems (WebSocket)
- Full-stack development
- Audio processing
- Privacy-first design
- Cost optimization

Great for interviews at companies building voice/translation products, international apps, or accessibility tools!
