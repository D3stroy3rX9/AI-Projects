# Audio Auto-Translator - Local Setup Guide

Complete step-by-step guide to get the Audio Auto-Translator running on your local machine.

---

## Prerequisites Installed ✅

Based on your system, you have:
- ✅ Python 3.13.9
- ✅ Node.js v22.18.0
- ✅ pnpm 10.24.0
- ✅ Docker 29.0.1

---

## Step-by-Step Setup

### 1. Navigate to Project Directory

```bash
cd /home/user/AI-Projects/audio-translator
```

### 2. Start PostgreSQL Database

**Important:** Docker Compose v2 uses `docker compose` (with space), not `docker-compose`.

```bash
# Start Docker daemon (if not already running)
# On Linux:
sudo systemctl start docker
# On macOS: Start Docker Desktop
# On Windows: Start Docker Desktop

# Start PostgreSQL container
docker compose up -d

# Verify it's running
docker compose ps
```

**Expected Output:**
```
NAME                    COMMAND                  SERVICE     STATUS       PORTS
audio-translator-db     "docker-entrypoint.s…"   postgres    Up 5 seconds 0.0.0.0:5432->5432/tcp
```

**Troubleshooting:**
- If `docker compose` doesn't work, try `docker-compose` (older Docker versions)
- If Docker daemon isn't running, start Docker Desktop or run `sudo systemctl start docker`
- If port 5432 is in use, change the port in `docker-compose.yml` (e.g., `5433:5432`)

### 3. Set Up Environment Variables

#### Backend Environment Variables

```bash
# Navigate to API directory
cd apps/api

# Copy example env file
cp .env.example .env
```

**Edit `apps/api/.env`:**
```env
DATABASE_URL=postgresql://translator:translator_password@localhost:5432/audio_translator
WHISPER_MODEL=base
TRANSLATION_BACKEND=libretranslate
LIBRETRANSLATE_URL=https://libretranslate.de
CORS_ORIGINS=http://localhost:3000
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
```

#### Frontend Environment Variables

```bash
# Navigate to web directory
cd ../web

# Copy example env file
cp .env.local.example .env.local
```

**Edit `apps/web/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/translate
```

### 4. Set Up Backend (Python)

```bash
# Navigate to API directory
cd ../../apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install ffmpeg (required for audio processing)
# On macOS:
brew install ffmpeg
# On Ubuntu/Debian:
sudo apt-get install ffmpeg
# On Windows: Download from https://ffmpeg.org/

# Run database migrations
alembic upgrade head

# Download Whisper model (happens automatically on first use, or run manually)
python download_models.py --model base
```

### 5. Set Up Frontend (Next.js)

Open a **new terminal** (keep backend terminal for later):

```bash
# Navigate to web directory
cd /home/user/AI-Projects/audio-translator/apps/web

# Install dependencies
pnpm install
```

### 6. Start the Application

#### Terminal 1 - Backend (FastAPI)

```bash
cd /home/user/AI-Projects/audio-translator/apps/api

# Activate venv if not already active
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Start backend server
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Backend will be available at: **http://localhost:8000**

#### Terminal 2 - Frontend (Next.js)

```bash
cd /home/user/AI-Projects/audio-translator/apps/web

# Start frontend dev server
pnpm dev
```

**Expected Output:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

Frontend will be available at: **http://localhost:3000**

---

## Verification Steps

### 1. Test Backend API

Open browser and visit:
- **Health Check:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Languages Endpoint:** http://localhost:8000/languages

**Expected Response from Health Check:**
```json
{
  "status": "ok",
  "models_loaded": true,
  "message": "Audio Auto-Translator API is running",
  "version": "0.3.0",
  "database": "connected"
}
```

### 2. Test Frontend

Open browser and visit: **http://localhost:3000**

You should see:
- Audio Auto-Translator interface
- Recording button
- Language selector (source and target)
- Translation display area
- History sidebar

### 3. Test End-to-End Flow

1. Click the **Record** button
2. Speak something (e.g., "Hello, how are you?")
3. Click **Stop Recording**
4. Wait for transcription to appear (2-10 seconds)
5. Wait for translation to appear (1-3 seconds)
6. Verify translation displays correctly
7. Click **Play** button to hear TTS
8. Check that translation appears in History sidebar

**If everything works:** ✅ Setup complete!

---

## Common Issues & Solutions

### Issue 1: Docker PostgreSQL Not Starting

**Error:** `docker compose: command not found`

**Solution:**
```bash
# Try with hyphen (older Docker versions)
docker-compose up -d

# Or install Docker Compose v2
sudo apt-get install docker-compose-plugin  # Linux
```

**Error:** `Cannot connect to the Docker daemon`

**Solution:**
```bash
# Start Docker daemon
sudo systemctl start docker  # Linux
# Or start Docker Desktop on macOS/Windows
```

**Error:** `port 5432 already in use`

**Solution:**
```bash
# Option 1: Stop existing PostgreSQL
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # macOS

# Option 2: Change port in docker-compose.yml
# Edit line 13: "5433:5432" instead of "5432:5432"
# Then update DATABASE_URL: localhost:5433 instead of localhost:5432
```

### Issue 2: Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
```bash
# Verify PostgreSQL is running
docker compose ps

# Check DATABASE_URL in .env matches docker-compose.yml
# Should be: postgresql://translator:translator_password@localhost:5432/audio_translator
```

**Error:** `ffmpeg: command not found`

**Solution:**
```bash
# Install ffmpeg
brew install ffmpeg           # macOS
sudo apt install ffmpeg       # Ubuntu/Debian
choco install ffmpeg          # Windows (Chocolatey)
# Or download from: https://ffmpeg.org/download.html
```

### Issue 3: Frontend Won't Start

**Error:** `Error: Cannot find module 'next'`

**Solution:**
```bash
# Reinstall dependencies
cd apps/web
rm -rf node_modules
pnpm install
```

**Error:** `Port 3000 is already in use`

**Solution:**
```bash
# Option 1: Kill process on port 3000
lsof -ti:3000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :3000   # Windows (then use Task Manager)

# Option 2: Use different port
pnpm dev -p 3001
```

### Issue 4: API Connection Errors in Browser

**Error:** `Failed to fetch` or CORS errors

**Solution:**
```bash
# Verify backend is running at http://localhost:8000
curl http://localhost:8000

# Check CORS_ORIGINS in apps/api/.env includes:
CORS_ORIGINS=http://localhost:3000

# Restart backend after changing .env
```

### Issue 5: WebSocket Connection Fails

**Error:** `WebSocket connection failed`

**Solution:**
- Verify `NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/translate` in `apps/web/.env.local`
- Check browser console for specific WebSocket errors
- Restart both backend and frontend

### Issue 6: Whisper Model Not Loading

**Error:** `Whisper model not loaded`

**Solution:**
```bash
# Manually download model
cd apps/api
python download_models.py --model base

# Wait for download to complete (74MB)
# Model will be cached in ~/.cache/whisper/
```

---

## Quick Commands Reference

### Docker Commands

```bash
# Start PostgreSQL
docker compose up -d

# Stop PostgreSQL
docker compose down

# View logs
docker compose logs -f postgres

# Restart PostgreSQL
docker compose restart

# Remove everything (including data)
docker compose down -v
```

### Backend Commands

```bash
# Start backend
cd apps/api
source venv/bin/activate
uvicorn main:app --reload

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head
```

### Frontend Commands

```bash
# Start frontend
cd apps/web
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run linter
pnpm lint

# Run tests (when implemented)
pnpm test
```

---

## Project URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation (Swagger):** http://localhost:8000/docs
- **API Documentation (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/

---

## Next Steps After Setup

1. **Test All Features:**
   - Main page (recording and translation)
   - Conversation page (/conversation)
   - History page (/history)
   - Settings page (/settings)
   - Dark mode toggle
   - TTS playback

2. **Run Tests:**
   ```bash
   cd apps/api
   pytest tests/ -v
   ```

3. **Read Documentation:**
   - `README.md` - Project overview
   - `DEPLOYMENT.md` - Production deployment
   - `API_DOCUMENTATION.md` - API reference
   - `PROMPT_*_VALIDATION.md` - Feature testing guides

4. **Deploy to Production (Optional):**
   - See `DEPLOYMENT.md` for Railway/Render/Vercel deployment

---

## Support

If you encounter any issues not covered here:

1. Check the troubleshooting sections in:
   - This guide (`SETUP_GUIDE.md`)
   - Main README (`README.md`)
   - Deployment guide (`DEPLOYMENT.md`)
   - Validation guides (`PROMPT_*_VALIDATION.md`)

2. Check logs:
   - Backend: Terminal running uvicorn
   - Frontend: Terminal running `pnpm dev`
   - PostgreSQL: `docker compose logs -f postgres`
   - Browser: Developer Console (F12)

3. Verify all services are running:
   - PostgreSQL: `docker compose ps`
   - Backend: `curl http://localhost:8000`
   - Frontend: Open http://localhost:3000

---

**Happy translating! 🎤🌍**
