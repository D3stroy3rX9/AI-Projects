# Project 6: Real-Time Audio Auto-Translator

**Difficulty:** Medium
**Time:** 6-8 hours
**Cost:** $0 (100% free tier)

---

## Overview

A real-time voice translation application that listens to speech in one language and instantly translates it to another. Perfect for travel, language learning, international meetings, or customer support.

**What it does:**
- Speak into microphone in any language
- Real-time transcription with auto language detection
- Instant translation to 100+ languages
- Optional text-to-speech playback of translation
- Conversation mode (two-way translation)
- Save and export conversation history

**Real-world applications:**
- Travel conversations with locals
- International business meetings
- Language learning practice
- Customer support calls
- Live podcast/video translation
- Accessible communication for multilingual teams

---

## Why This Project Stands Out

### 1. **Immediately Useful**
- Everyone travels or communicates across languages
- Solves real pain point (language barriers)
- Can use it yourself daily for learning

### 2. **Impressive Tech Stack**
- OpenAI Whisper (state-of-the-art speech recognition)
- Meta NLLB-200 (200+ language translation)
- Real-time audio processing
- WebSocket streaming

### 3. **Portfolio Value**
- Shows full audio pipeline: speech → text → translation → speech
- Demonstrates ML model integration (Whisper + NLLB)
- Real-time system design
- Privacy-focused (100% local/offline capable)

### 4. **Zero Cost**
- All models run locally (no API fees)
- Open-source stack (Whisper, NLLB, LibreTranslate)
- Can deploy on free tiers
- No recurring costs

### 5. **Interview Talking Points**
- "Built real-time voice translator supporting 100+ languages"
- "Deployed Whisper and NLLB models with CPU-only inference"
- "Achieved <5 second latency for transcription + translation"
- "Zero API costs using local models vs $0.006/min for Google Translate API"
- "Privacy-first design - all processing happens locally"

---

## Tech Stack

### Frontend
- **Next.js 14** with TypeScript
- **TailwindCSS** for styling
- **Web Audio API** for microphone capture
- **MediaRecorder API** for audio recording
- **Web Speech API** for text-to-speech (fallback: gTTS)
- **WebSocket** for real-time streaming

### Backend
- **Python FastAPI** (async web framework)
- **OpenAI Whisper** (speech-to-text)
  - Model: `whisper-base` (74MB, CPU-friendly)
  - Supports 99 languages with auto-detection
  - ~5-10 seconds on CPU for 30-second audio
- **Meta NLLB-200** (translation)
  - Model: `nllb-200-distilled-600M` (1.2GB)
  - 200 languages, 40,000+ translation pairs
  - ~2-5 seconds per sentence on CPU
- **Alternative:** LibreTranslate API (free tier, easier setup)

### Database
- **PostgreSQL** (conversation history)
- **SQLite** (development, simpler alternative)

### Infrastructure
- **Docker** + Docker Compose (local development)
- **Redis** (optional, for caching translations)
- **Nginx** (optional, reverse proxy)

### Deployment
- **Backend:** Railway/Render free tier ($5 credit)
- **Frontend:** Vercel (unlimited free)
- **Models:** Run on same backend server (CPU)

---

## Key Features

### Core Features (MVP)
1. **Voice Recording**
   - Click-to-record interface
   - Auto-stop after silence detection
   - Visual audio waveform
   - Recording timer

2. **Speech-to-Text**
   - Real-time transcription using Whisper
   - Auto language detection (99 languages)
   - Display confidence scores
   - Show detected language

3. **Translation**
   - Select target language from 100+ options
   - Instant translation display
   - Side-by-side original + translation
   - Confidence scoring

4. **Text-to-Speech**
   - Click to hear translation
   - Adjustable playback speed
   - Multiple voice options
   - Pause/resume controls

### Advanced Features
5. **Conversation Mode**
   - Two-way translation (Person A ↔ Person B)
   - Alternating languages
   - Split-screen interface
   - Color-coded speakers

6. **History & Export**
   - Save all conversations to database
   - Search past translations
   - Export as TXT, JSON, or PDF
   - Timestamp tracking

7. **Offline Mode**
   - Download models for offline use
   - PWA (Progressive Web App)
   - Works on mobile without internet
   - Cache frequently used translations

8. **Smart Features**
   - Detect and preserve names, numbers, acronyms
   - Context-aware translation
   - Profanity filter (optional)
   - Formality level (casual vs formal)

---

## Architecture

### High-Level Flow
```
User speaks → Browser captures audio → WebSocket → Backend
                                                     ↓
                                            Whisper transcribes
                                                     ↓
                                            Detect source language
                                                     ↓
                                            NLLB translates
                                                     ↓
                                            Save to database
                                                     ↓
                                Stream back to frontend → Display + TTS
```

### Component Architecture
```
┌─────────────────────────────────────────┐
│           Frontend (Next.js)            │
│  ┌─────────────┐    ┌─────────────┐    │
│  │ Audio Input │    │ Translation │    │
│  │   Module    │───▶│   Display   │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │           │
│         ▼                   ▼           │
│  ┌─────────────┐    ┌─────────────┐    │
│  │  WebSocket  │    │     TTS     │    │
│  │   Client    │    │   Module    │    │
│  └─────────────┘    └─────────────┘    │
└──────────┬──────────────────────────────┘
           │
    WebSocket Connection
           │
┌──────────▼──────────────────────────────┐
│         Backend (FastAPI)               │
│  ┌─────────────┐    ┌─────────────┐    │
│  │  WebSocket  │───▶│   Whisper   │    │
│  │   Server    │    │   Service   │    │
│  └─────────────┘    └─────────────┘    │
│                            │            │
│                            ▼            │
│                     ┌─────────────┐    │
│                     │    NLLB     │    │
│                     │   Service   │    │
│                     └─────────────┘    │
│                            │            │
│                            ▼            │
│                     ┌─────────────┐    │
│                     │  Database   │    │
│                     │   (Postgres)│    │
│                     └─────────────┘    │
└─────────────────────────────────────────┘
```

### Data Flow
1. **Audio Capture:** Browser MediaRecorder → WebM audio blob
2. **Upload:** WebSocket sends audio chunks to backend
3. **Transcription:** Whisper processes audio → text + detected language
4. **Translation:** NLLB translates text → target language
5. **Storage:** Save to PostgreSQL (conversation, timestamp, languages)
6. **Response:** Stream back transcription + translation via WebSocket
7. **Display:** Frontend shows both texts side-by-side
8. **TTS (optional):** Browser speaks translation using Web Speech API

---

## Model Details

### Whisper (Speech Recognition)

**What it is:**
- OpenAI's state-of-the-art speech recognition model
- Trained on 680,000 hours of multilingual data
- Open-source (MIT license)

**Model Options:**
| Model | Size | Speed (CPU) | Quality | Use Case |
|-------|------|-------------|---------|----------|
| tiny | 39MB | 2-3s | Good | Fast, resource-constrained |
| base | 74MB | 5-10s | Better | **Recommended** (balanced) |
| small | 244MB | 15-20s | Best | High accuracy needed |
| medium | 769MB | 30-40s | Excellent | Quality over speed |

**We'll use `base`** - best balance of speed and accuracy for CPU.

**Capabilities:**
- ✅ Auto language detection (99 languages)
- ✅ Handles accents and dialects
- ✅ Robust to background noise
- ✅ Punctuation and capitalization
- ✅ Word-level timestamps

### NLLB-200 (Translation)

**What it is:**
- Meta's "No Language Left Behind" model
- 200 languages, 40,000+ translation pairs
- Open-source (CC BY-NC 4.0)

**Model Options:**
| Model | Size | Speed (CPU) | Languages | Use Case |
|-------|------|-------------|-----------|----------|
| distilled-600M | 1.2GB | 2-5s/sentence | 200 | **Recommended** |
| 1.3B | 2.6GB | 5-10s/sentence | 200 | Better quality |
| 3.3B | 6.6GB | 10-20s/sentence | 200 | Best quality |

**We'll use `distilled-600M`** - runs on CPU, good quality.

**Supported Languages (sample):**
- European: English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, etc.
- Asian: Chinese, Japanese, Korean, Hindi, Thai, Vietnamese, Indonesian, etc.
- Middle Eastern: Arabic, Hebrew, Persian, Turkish, Urdu, etc.
- African: Swahili, Zulu, Yoruba, Hausa, Amharic, etc.
- Others: Russian, Ukrainian, Greek, Swedish, Finnish, etc.

### Alternative: LibreTranslate (Easier Setup)

**What it is:**
- Free, open-source translation API
- 30+ languages
- Can self-host or use public instance

**Pros:**
- Easy API integration (no model downloads)
- Fast (offloads compute)
- Free public instance available

**Cons:**
- Only 30 languages (vs NLLB's 200)
- Requires internet connection
- Public instance has rate limits

**Use case:** Start with LibreTranslate API, migrate to NLLB later

---

## Performance Metrics

### Target Performance
- **Transcription latency:** <10 seconds for 30-second audio
- **Translation latency:** <5 seconds per sentence
- **Total end-to-end:** <15 seconds from speaking to seeing translation
- **Audio quality:** Support 16kHz+ sample rate
- **Accuracy:** >85% translation quality (BLEU score)

### Resource Requirements
- **CPU:** 2+ cores (4+ recommended)
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 2GB for models
- **Bandwidth:** Minimal (audio upload only)

### Scalability
- **Concurrent users:** 10-20 on free tier (CPU bottleneck)
- **Cache hit rate:** 40-60% (common phrases)
- **Database:** Handles 100k+ translations easily

---

## Success Metrics

### Technical
- ✅ Transcription accuracy >90% for clear speech
- ✅ Translation BLEU score >30 for common languages
- ✅ End-to-end latency <15 seconds
- ✅ Support 50+ languages in production
- ✅ Runs on CPU (no GPU required)

### User Experience
- ✅ Intuitive one-click recording
- ✅ Real-time visual feedback (waveform, loading states)
- ✅ Smooth playback of translations
- ✅ Mobile-responsive design
- ✅ Offline mode works reliably

### Cost
- ✅ Zero API costs (local models)
- ✅ Stays within free tier (Railway $5 credit)
- ✅ No ongoing subscription fees

---

## Comparison to Existing Solutions

| Feature | Google Translate | iTranslate | Our App |
|---------|-----------------|-----------|---------|
| Voice input | ✅ | ✅ | ✅ |
| Languages | 133 | 100+ | 200 (NLLB) |
| Offline mode | Limited | Paid ($5/mo) | ✅ Free |
| Privacy | Sends to cloud | Sends to cloud | 100% local |
| Cost | Free (with ads) | $5-10/mo | $0 forever |
| Conversation mode | ✅ | ✅ | ✅ |
| Export history | ❌ | ✅ | ✅ |
| Custom models | ❌ | ❌ | ✅ (swap models) |
| Open source | ❌ | ❌ | ✅ |

**Our competitive advantage:**
1. **Privacy:** No data sent to external servers
2. **Cost:** 100% free, no ads or subscriptions
3. **Flexibility:** Swap models, add languages, customize
4. **Learning:** Full control over tech stack

---

## Engineering Challenges

### 1. **Audio Quality**
- Challenge: Microphone quality varies across devices
- Solution: Noise reduction preprocessing, min sample rate requirements

### 2. **Latency**
- Challenge: Users expect near real-time translation
- Solution: Optimize models (distilled versions), async processing, streaming

### 3. **Language Detection Accuracy**
- Challenge: Whisper might misdetect similar languages
- Solution: Allow manual language selection, show confidence scores

### 4. **Context Loss**
- Challenge: Translating sentence-by-sentence loses context
- Solution: Maintain conversation context, use previous sentences for context

### 5. **Model Size**
- Challenge: NLLB is 1.2GB (slow initial load)
- Solution: Cache models, lazy loading, progress indicators

### 6. **CPU Performance**
- Challenge: Models run slow on CPU
- Solution: Use distilled models, batching, caching common translations

---

## Future Enhancements

### Phase 2 (Post-MVP)
- **Streaming transcription:** Show words as they're spoken
- **Multi-speaker detection:** Identify different speakers
- **Accent adaptation:** Fine-tune Whisper on specific accents
- **Video translation:** Translate YouTube/video files

### Phase 3 (Advanced)
- **Custom vocabulary:** Add domain-specific terms (medical, legal)
- **Dialect support:** Regional variants (es-MX vs es-ES)
- **Emotional tone:** Preserve emotion in translation
- **Live call translation:** Integrate with phone calls

### Phase 4 (Enterprise)
- **Team collaboration:** Shared translation memory
- **API for developers:** Expose as translation API
- **Metrics dashboard:** Usage analytics, accuracy tracking
- **Admin panel:** Manage users, monitor resources

---

## Learning Outcomes

By building this project, you'll learn:

### ML/AI
- ✅ Integrating pre-trained models (Whisper, NLLB)
- ✅ Audio processing and feature extraction
- ✅ Model optimization for CPU inference
- ✅ Evaluation metrics (BLEU, WER)

### Backend
- ✅ WebSocket real-time communication
- ✅ Async Python (FastAPI)
- ✅ File upload handling (audio)
- ✅ Background task processing

### Frontend
- ✅ Web Audio API (microphone access)
- ✅ MediaRecorder API (audio recording)
- ✅ WebSocket client implementation
- ✅ Real-time UI updates

### DevOps
- ✅ Docker multi-stage builds
- ✅ Model deployment strategies
- ✅ Resource optimization (CPU-bound workloads)
- ✅ Free-tier deployment

---

## Repository Structure

```
audio-translator/
├── apps/
│   ├── web/                    # Next.js frontend
│   │   ├── app/
│   │   │   ├── page.tsx       # Main translator UI
│   │   │   ├── history/       # Conversation history
│   │   │   └── settings/      # Language preferences
│   │   ├── components/
│   │   │   ├── AudioRecorder.tsx
│   │   │   ├── TranslationDisplay.tsx
│   │   │   ├── LanguageSelector.tsx
│   │   │   └── TTSPlayer.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useAudioRecorder.ts
│   │   │   └── useTTS.ts
│   │   └── package.json
│   │
│   └── api/                    # Python FastAPI backend
│       ├── main.py            # FastAPI app + WebSocket
│       ├── services/
│       │   ├── whisper_service.py
│       │   ├── translation_service.py
│       │   └── tts_service.py
│       ├── models/            # Downloaded ML models
│       │   ├── whisper-base/
│       │   └── nllb-distilled-600m/
│       ├── db/
│       │   ├── database.py
│       │   └── models.py      # SQLAlchemy models
│       ├── tests/
│       └── requirements.txt
│
├── packages/                   # Shared code (optional)
│   └── types/                 # TypeScript types
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Getting Started

See **PROJECT_6_BUILD_GUIDE.md** for the complete 8-prompt implementation guide.

### Quick Start
```bash
# Clone repo
git clone <your-repo>
cd audio-translator

# Backend setup
cd apps/api
pip install -r requirements.txt
python download_models.py  # Download Whisper + NLLB
uvicorn main:app --reload

# Frontend setup (new terminal)
cd apps/web
pnpm install
pnpm dev

# Open http://localhost:3000
# Click "Record" and start speaking!
```

---

## License

MIT (code) + Model licenses:
- Whisper: MIT License
- NLLB-200: CC BY-NC 4.0 (non-commercial)

For commercial use, consider:
- Helsinki-NLP models (Apache 2.0)
- LibreTranslate (AGPL-3.0)

---

## Resources

### Documentation
- [Whisper GitHub](https://github.com/openai/whisper)
- [NLLB HuggingFace](https://huggingface.co/facebook/nllb-200-distilled-600M)
- [LibreTranslate](https://libretranslate.com/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

### Tutorials
- [Whisper Python API](https://github.com/openai/whisper#python-usage)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Next.js Audio Recording](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API)

---

**Ready to build?** Head to **PROJECT_6_BUILD_GUIDE.md** for the complete step-by-step guide with 8 Claude Code prompts!
