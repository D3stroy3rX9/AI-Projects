# 🎤 Audio Auto-Translator

Real-time voice translation application supporting 100+ languages using OpenAI Whisper and LibreTranslate/NLLB.

## Features

- 🎤 **Voice Recording** - Click-to-record with auto-stop on silence
- 🌍 **100+ Languages** - Translate between 200 language pairs
- 🔊 **Text-to-Speech** - Hear translations in native pronunciation
- 💬 **Conversation Mode** - Two-way translation for real conversations
- 📝 **History & Export** - Save and export conversation history
- 🔒 **Privacy-First** - 100% local processing (optional)
- 💰 **Zero Cost** - Free tier compatible, no API keys required

## Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first styling
- **Web Audio API** - Microphone capture
- **WebSocket** - Real-time communication

### Backend
- **FastAPI** - Modern Python web framework
- **OpenAI Whisper** - State-of-the-art speech recognition
- **LibreTranslate/NLLB** - Translation engine
- **PostgreSQL** - Database for history
- **SQLAlchemy** - ORM and migrations

### ML Models
- **Whisper (base)** - 74MB, CPU-friendly, 99 languages
- **NLLB-200** - 1.2GB, 200 languages (optional)
- **LibreTranslate API** - Free public instance (default)

## Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **pnpm** - Install: `npm install -g pnpm`
- **Docker** (optional) - [Download](https://www.docker.com/get-started)
- **8GB+ RAM** - Recommended for running models

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd audio-translator
```

### 2. Set Up Environment Variables

```bash
# Root directory
cp .env.example .env

# Backend
cp apps/api/.env.example apps/api/.env

# Frontend
cp apps/web/.env.local.example apps/web/.env.local
```

### 3. Start PostgreSQL Database

```bash
docker-compose up -d
```

Verify it's running:
```bash
docker ps
```

### 4. Set Up Backend (Python)

```bash
cd apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download Whisper model (will be added in Prompt B)
# python download_models.py --model base

# Run the server
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000

### 5. Set Up Frontend (Next.js)

Open a new terminal:

```bash
cd apps/web

# Install dependencies
pnpm install

# Run development server
pnpm dev
```

Frontend will be available at: http://localhost:3000

### 6. Test the Setup

1. Open http://localhost:3000 in your browser
2. You should see the Audio Auto-Translator interface
3. Backend API docs: http://localhost:8000/docs

## Project Structure

```
audio-translator/
├── apps/
│   ├── web/                    # Next.js frontend
│   │   ├── app/
│   │   │   ├── layout.tsx     # Root layout
│   │   │   ├── page.tsx       # Main page
│   │   │   └── globals.css    # Global styles
│   │   ├── components/        # React components (to be added)
│   │   ├── hooks/             # Custom hooks (to be added)
│   │   └── package.json
│   │
│   └── api/                    # Python FastAPI backend
│       ├── main.py            # FastAPI app
│       ├── services/          # Business logic (to be added)
│       ├── db/                # Database models (to be added)
│       ├── utils/             # Helper functions (to be added)
│       ├── tests/             # Tests (to be added)
│       └── requirements.txt
│
├── docker-compose.yml         # PostgreSQL container
├── .env.example               # Environment template
├── .gitignore
└── README.md
```

## Environment Variables

### Backend (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `WHISPER_MODEL` | `base` | Whisper model size (tiny/base/small/medium) |
| `TRANSLATION_BACKEND` | `libretranslate` | Translation engine (libretranslate/nllb) |
| `LIBRETRANSLATE_URL` | `https://libretranslate.de` | LibreTranslate API endpoint |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend origins |

### Frontend (.env.local)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000` | WebSocket URL |

## Development

### Running Tests

Backend:
```bash
cd apps/api
pytest tests/ -v
```

Frontend:
```bash
cd apps/web
pnpm test
```

### Database Migrations

```bash
cd apps/api

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Model Downloads

Whisper models are downloaded automatically on first use, or manually:

```bash
cd apps/api
python download_models.py --model base
```

Available models:
- `tiny` - 39MB, fastest, lower accuracy
- `base` - 74MB, balanced (recommended)
- `small` - 244MB, high accuracy
- `medium` - 769MB, best accuracy

## Deployment

### Backend (Railway/Render)

1. Connect your GitHub repository
2. Set environment variables from `.env.example`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Connect your GitHub repository
2. Root directory: `apps/web`
3. Build command: `pnpm build`
4. Set `NEXT_PUBLIC_WS_URL` to your backend WebSocket URL

## Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker ps

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Port Already in Use

```bash
# Kill process on port 8000 (backend)
# Linux/macOS:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000

# Kill process on port 3000 (frontend)
# Linux/macOS:
lsof -ti:3000 | xargs kill -9
```

### Model Download Fails

```bash
# Install ffmpeg (required for audio processing)
# macOS:
brew install ffmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg
# Windows: Download from https://ffmpeg.org/
```

## Next Steps

This is **Prompt A** - Project Scaffold complete! ✅

Continue with:
- **Prompt B** - Database Models & Core Backend Setup
- **Prompt C** - Whisper Integration & Audio Processing
- **Prompt D** - Translation Service Integration
- **Prompt E** - Frontend Audio Recording & WebSocket
- **Prompt F** - Text-to-Speech & History
- **Prompt G** - Conversation Mode & UI Polish
- **Prompt H** - Testing, Documentation & Deployment

## License

MIT License - See LICENSE file for details

### Model Licenses
- **Whisper**: MIT License
- **NLLB-200**: CC BY-NC 4.0 (non-commercial)
- **LibreTranslate**: AGPL-3.0

For commercial use, consider using Helsinki-NLP models (Apache 2.0) or self-hosted LibreTranslate.

## Resources

- [Whisper GitHub](https://github.com/openai/whisper)
- [NLLB HuggingFace](https://huggingface.co/facebook/nllb-200-distilled-600M)
- [LibreTranslate](https://libretranslate.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check existing documentation
- Review the troubleshooting section

---

**Built with ❤️ for real-time multilingual communication**
