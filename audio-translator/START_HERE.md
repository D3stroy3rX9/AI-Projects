# 🎤 Audio Auto-Translator - START HERE

Welcome to the Audio Auto-Translator! This guide will get you started quickly.

---

## 📋 Quick Navigation

| What do you want to do? | Read this |
|-------------------------|-----------|
| 🆕 **First time setup** | `QUICKSTART.md` or run `./setup.sh` |
| 🚀 **Start the app** (daily) | `STARTUP_GUIDE.md` or use helper scripts below |
| 📖 **Learn about features** | `README.md` |
| 🔧 **Troubleshoot issues** | `SETUP_GUIDE.md` |
| 📡 **API reference** | `API_DOCUMENTATION.md` |
| ☁️ **Deploy to production** | `DEPLOYMENT.md` |

---

## ⚡ Super Quick Start

### First Time Setup (5-10 minutes)

```bash
cd /home/user/AI-Projects/audio-translator
./setup.sh  # Linux/macOS
# OR
setup.bat   # Windows
```

This will automatically set up everything you need!

---

### Daily Startup (After Setup)

**Option 1: Use Helper Scripts (Easiest)**

```bash
# Terminal 1 - Start Backend
./start-backend.sh   # Linux/macOS
# OR
start-backend.bat    # Windows

# Terminal 2 - Start Frontend (open new terminal)
./start-frontend.sh  # Linux/macOS
# OR
start-frontend.bat   # Windows
```

**Option 2: Manual Commands**

```bash
# Terminal 1 - Backend
cd apps/api
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload

# Terminal 2 - Frontend
cd apps/web
pnpm dev
```

**Then open:** http://localhost:3000

---

## 🛑 Stop Everything

```bash
./stop-all.sh   # Linux/macOS
# OR
stop-all.bat    # Windows
```

---

## 📚 Complete Documentation

### Setup & Startup
- **`QUICKSTART.md`** - Quick 5-minute setup guide
- **`SETUP_GUIDE.md`** - Comprehensive setup with troubleshooting (400+ lines)
- **`STARTUP_GUIDE.md`** - Daily startup/shutdown procedures

### Features & Usage
- **`README.md`** - Full project documentation, features, architecture
- **`PROMPT_*_VALIDATION.md`** - Testing guides for each feature set

### Technical Reference
- **`API_DOCUMENTATION.md`** - Complete API reference (40+ pages)
- **`DEPLOYMENT.md`** - Production deployment guide (60+ pages)

---

## 🎯 What This App Does

**Audio Auto-Translator** is a real-time translation app that:

1. 🎤 Records your voice in any language
2. 📝 Transcribes it to text using OpenAI Whisper
3. 🌍 Translates it to 100+ languages
4. 🔊 Reads it aloud using Text-to-Speech
5. 💾 Saves your translation history
6. 💬 Supports two-way conversations
7. 🌙 Has beautiful dark mode
8. ⚡ Works offline (after model download)

---

## 🔧 Helper Scripts

All scripts are located in the project root:

### Setup Scripts (First Time Only)
- `setup.sh` / `setup.bat` - Complete automated setup

### Startup Scripts (Daily Use)
- `start-backend.sh` / `start-backend.bat` - Start backend + database
- `start-frontend.sh` / `start-frontend.bat` - Start frontend
- `stop-all.sh` / `stop-all.bat` - Stop all services

---

## 🌐 Application URLs

Once running, access these URLs:

| Service | URL |
|---------|-----|
| **Main App** | http://localhost:3000 |
| **Conversation Mode** | http://localhost:3000/conversation |
| **History** | http://localhost:3000/history |
| **Settings** | http://localhost:3000/settings |
| **Backend API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |

---

## ⚠️ Common Issues

### "uvicorn: command not found"
```bash
cd apps/api
source venv/bin/activate  # Make sure you see (venv) in prompt
pip install -r requirements.txt
```

### "docker compose: command not found"
```bash
# Try with hyphen (older Docker)
docker-compose up -d

# Or start Docker Desktop
```

### "Port already in use"
```bash
# Stop existing processes
./stop-all.sh  # or stop-all.bat

# Or kill specific port
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

**For more troubleshooting, see `SETUP_GUIDE.md`**

---

## 🧪 Quick Test

1. Open http://localhost:3000
2. Click **"Record"**
3. Say: *"Hello, how are you?"*
4. Click **"Stop Recording"**
5. Wait for translation
6. Click **Play** to hear TTS
7. ✅ Success!

---

## 📦 Tech Stack

- **Frontend:** Next.js 14, React, TypeScript, TailwindCSS
- **Backend:** FastAPI (Python), SQLAlchemy, Alembic
- **AI/ML:** OpenAI Whisper (speech-to-text)
- **Translation:** LibreTranslate (offline-capable)
- **Database:** PostgreSQL
- **TTS:** Web Speech API (browser-native)

---

## 🚀 Production Ready

This project is production-ready with:
- ✅ Complete test suite (pytest)
- ✅ Database migrations (Alembic)
- ✅ API documentation (Swagger/ReDoc)
- ✅ Deployment guides (Railway/Render/Vercel)
- ✅ Error handling & logging
- ✅ CORS & WebSocket support
- ✅ PWA support (installable)
- ✅ Dark mode

---

## 🎓 Learning Path

1. **Day 1:** Run setup, test basic translation
2. **Day 2:** Try all features (conversation, history, settings)
3. **Day 3:** Read `README.md` to understand architecture
4. **Day 4:** Read `API_DOCUMENTATION.md` to understand APIs
5. **Day 5:** Deploy to production using `DEPLOYMENT.md`

---

## 🤝 Need Help?

1. **Setup issues:** Check `SETUP_GUIDE.md` troubleshooting section
2. **Startup issues:** Check `STARTUP_GUIDE.md` troubleshooting section
3. **Feature questions:** Check `README.md` features section
4. **API questions:** Check `API_DOCUMENTATION.md`
5. **Deployment questions:** Check `DEPLOYMENT.md`

---

## ⌨️ Keyboard Shortcuts

- **Space** - Start/stop recording
- **Ctrl+Enter** - Translate
- **Ctrl+Shift+D** - Toggle dark mode
- **Escape** - Stop TTS playback

---

## 📊 Project Status

✅ **All 8 Prompts Complete**

- ✅ Prompt A: Project Setup & Foundation
- ✅ Prompt B: Core Translation Engine
- ✅ Prompt C: Audio Recording
- ✅ Prompt D: Real-time WebSocket
- ✅ Prompt E: Language Detection
- ✅ Prompt F: Text-to-Speech & History
- ✅ Prompt G: Conversation Mode & UI Polish
- ✅ Prompt H: Testing, Documentation & Deployment

**Status:** Production Ready 🎉

---

## 🎯 Next Steps

1. ✅ Run `./setup.sh` (if not done)
2. ✅ Run `./start-backend.sh` + `./start-frontend.sh`
3. ✅ Test at http://localhost:3000
4. 📖 Read `README.md` for full documentation
5. 🚀 Deploy using `DEPLOYMENT.md` (optional)

---

**Happy translating! 🎤🌍**

**Questions?** Check the documentation files listed above!
