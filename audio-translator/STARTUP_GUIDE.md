# Audio Auto-Translator - Startup Guide

Quick reference for starting and stopping the application after initial setup is complete.

---

## 🚀 Daily Startup (After Setup)

### Step 1: Start PostgreSQL Database

```bash
cd /home/user/AI-Projects/audio-translator
docker compose up -d
```

**Verify it's running:**
```bash
docker compose ps
```

**Expected output:**
```
NAME                    SERVICE     STATUS       PORTS
audio-translator-db     postgres    Up 5 seconds 0.0.0.0:5432->5432/tcp
```

---

### Step 2: Start Backend (Terminal 1)

```bash
# Navigate to API directory
cd /home/user/AI-Projects/audio-translator/apps/api

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Start backend server
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is running at: http://localhost:8000**

**Leave this terminal open!**

---

### Step 3: Start Frontend (Terminal 2)

Open a **new terminal window** and run:

```bash
# Navigate to web directory
cd /home/user/AI-Projects/audio-translator/apps/web

# Start frontend dev server
pnpm dev
```

**Expected output:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

✅ **Frontend is running at: http://localhost:3000**

**Leave this terminal open!**

---

## 🌐 Access the Application

Open your browser and visit:

- **Main App:** http://localhost:3000
- **API Health Check:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

## 🧪 Quick Test

1. Go to http://localhost:3000
2. Click **"Record"** button
3. Say something (e.g., "Hello")
4. Click **"Stop Recording"**
5. Wait for transcription and translation
6. ✅ Success!

---

## 🛑 Shutdown

When you're done working:

### Stop Frontend (Terminal 2)
```
Press: Ctrl+C
```

### Stop Backend (Terminal 1)
```
Press: Ctrl+C
```

### Stop PostgreSQL
```bash
cd /home/user/AI-Projects/audio-translator
docker compose down
```

**Optional: Stop but keep data**
```bash
docker compose stop  # Stops containers but keeps data
```

**Optional: Stop and remove all data**
```bash
docker compose down -v  # CAUTION: Deletes all database data!
```

---

## 📝 One-Command Startup Scripts

### Create Quick Start Scripts

For even faster startup, create these helper scripts:

#### **`start-all.sh`** (Linux/macOS)

```bash
#!/bin/bash
cd /home/user/AI-Projects/audio-translator

echo "Starting PostgreSQL..."
docker compose up -d

echo "Starting Backend and Frontend..."
echo "Open two terminals and run:"
echo "  Terminal 1: cd apps/api && source venv/bin/activate && uvicorn main:app --reload"
echo "  Terminal 2: cd apps/web && pnpm dev"
```

#### **`start-all.bat`** (Windows)

```cmd
@echo off
cd /home/user/AI-Projects/audio-translator

echo Starting PostgreSQL...
docker compose up -d

echo Starting Backend and Frontend...
echo Open two terminals and run:
echo   Terminal 1: cd apps\api && venv\Scripts\activate && uvicorn main:app --reload
echo   Terminal 2: cd apps\web && pnpm dev
```

---

## 🔄 Alternative: Run Backend in Background

If you want to run everything from one terminal:

```bash
# Start PostgreSQL
docker compose up -d

# Start backend in background
cd apps/api
source venv/bin/activate
nohup uvicorn main:app > backend.log 2>&1 &
echo $! > backend.pid  # Save process ID

# Start frontend (foreground)
cd ../web
pnpm dev
```

**To stop backend later:**
```bash
kill $(cat apps/api/backend.pid)
```

---

## 🔧 Troubleshooting

### Issue: "docker compose: command not found"

**Try:**
```bash
docker-compose up -d  # Older Docker versions use hyphen
```

**Or start Docker Desktop** (macOS/Windows)

---

### Issue: "uvicorn: command not found"

**Fix:**
```bash
# Make sure virtual environment is activated
cd apps/api
source venv/bin/activate  # You should see (venv) in prompt

# If still not working, reinstall
pip install uvicorn[standard]

# Or run as Python module
python -m uvicorn main:app --reload
```

---

### Issue: "Port 5432 already in use"

**Fix:**
```bash
# Check what's using port 5432
sudo lsof -i :5432  # Linux/macOS
netstat -ano | findstr :5432  # Windows

# Stop existing PostgreSQL
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # macOS

# Or change port in docker-compose.yml to 5433:5432
```

---

### Issue: "Port 8000 already in use"

**Fix:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Linux/macOS
netstat -ano | findstr :8000   # Windows (then kill from Task Manager)

# Or use different port
uvicorn main:app --reload --port 8001
# Then update NEXT_PUBLIC_API_URL in apps/web/.env.local
```

---

### Issue: "Port 3000 already in use"

**Fix:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9  # Linux/macOS

# Or use different port
pnpm dev -p 3001  # Runs on port 3001 instead
```

---

### Issue: Backend starts but shows errors in log

**Common fixes:**

1. **Database connection error:**
   ```bash
   # Verify PostgreSQL is running
   docker compose ps

   # Check DATABASE_URL in apps/api/.env
   # Should be: postgresql://translator:translator_password@localhost:5432/audio_translator
   ```

2. **Missing Whisper model:**
   ```bash
   cd apps/api
   source venv/bin/activate
   python -c "import whisper; whisper.load_model('base')"
   ```

3. **Missing dependencies:**
   ```bash
   cd apps/api
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

### Issue: Frontend starts but can't connect to backend

**Fix:**

1. **Verify backend is running:**
   ```bash
   curl http://localhost:8000
   # Should return: {"status":"ok",...}
   ```

2. **Check environment variables:**
   ```bash
   cat apps/web/.env.local
   # Should have:
   # NEXT_PUBLIC_API_URL=http://localhost:8000
   # NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/translate
   ```

3. **Restart frontend:**
   ```bash
   # In frontend terminal, press Ctrl+C then:
   pnpm dev
   ```

---

## 📊 System Status Checks

### Check All Services

```bash
# PostgreSQL
docker compose ps

# Backend (should see process listening on port 8000)
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Frontend (should see process listening on port 3000)
lsof -i :3000  # Linux/macOS
netstat -ano | findstr :3000  # Windows
```

### Check Service Health

```bash
# PostgreSQL
docker compose exec postgres pg_isready -U translator

# Backend API
curl http://localhost:8000
curl http://localhost:8000/languages

# Frontend (open in browser)
# http://localhost:3000
```

---

## ⚡ Pro Tips

### 1. Use Terminal Multiplexer (tmux/screen)

Run all services in one terminal window with split panes:

```bash
# Install tmux (if not installed)
brew install tmux  # macOS
sudo apt install tmux  # Ubuntu/Debian

# Start tmux session
tmux new -s audio-translator

# Split window horizontally (Ctrl+B then ")
# Split window vertically (Ctrl+B then %)
# Navigate between panes (Ctrl+B then arrow keys)

# Pane 1: Start backend
cd apps/api && source venv/bin/activate && uvicorn main:app --reload

# Pane 2: Start frontend
cd apps/web && pnpm dev

# Detach from tmux: Ctrl+B then D
# Reattach later: tmux attach -t audio-translator
```

### 2. Create Shell Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Audio Translator aliases
alias at-start-db='cd /home/user/AI-Projects/audio-translator && docker compose up -d'
alias at-start-backend='cd /home/user/AI-Projects/audio-translator/apps/api && source venv/bin/activate && uvicorn main:app --reload'
alias at-start-frontend='cd /home/user/AI-Projects/audio-translator/apps/web && pnpm dev'
alias at-stop='cd /home/user/AI-Projects/audio-translator && docker compose down'
```

Then reload: `source ~/.bashrc`

Now you can use:
```bash
at-start-db        # Start PostgreSQL
at-start-backend   # Start backend
at-start-frontend  # Start frontend
at-stop            # Stop everything
```

### 3. Auto-restart on File Changes

Both servers auto-restart when you make code changes:

- **Backend:** `--reload` flag enables auto-reload
- **Frontend:** Next.js dev server auto-reloads by default

Just save your file and the server will restart automatically!

### 4. View Logs

```bash
# PostgreSQL logs
docker compose logs -f postgres

# Backend logs (in terminal running uvicorn)
# Already visible in Terminal 1

# Frontend logs (in terminal running pnpm dev)
# Already visible in Terminal 2
```

---

## 📚 Related Documentation

- **First Time Setup:** `QUICKSTART.md` or `SETUP_GUIDE.md`
- **Full Documentation:** `README.md`
- **API Reference:** `API_DOCUMENTATION.md`
- **Deployment Guide:** `DEPLOYMENT.md`
- **Troubleshooting:** `SETUP_GUIDE.md` (Common Issues section)

---

## ✅ Startup Checklist

Use this checklist for daily startup:

- [ ] Start Docker Desktop (if on macOS/Windows)
- [ ] Run `docker compose up -d` (PostgreSQL)
- [ ] Verify PostgreSQL is running: `docker compose ps`
- [ ] Start backend in Terminal 1
- [ ] Verify backend health: Visit http://localhost:8000
- [ ] Start frontend in Terminal 2
- [ ] Verify frontend: Visit http://localhost:3000
- [ ] Test recording and translation
- [ ] ✅ All systems operational!

---

## 🎯 Summary

**Minimum required commands to start:**

```bash
# Terminal 0: Start PostgreSQL
docker compose up -d

# Terminal 1: Start Backend
cd apps/api && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2: Start Frontend
cd apps/web && pnpm dev

# Browser: Open http://localhost:3000
```

**To stop:**
```bash
# Press Ctrl+C in Terminal 1 and 2
# Then run: docker compose down
```

---

**Happy translating! 🎤🌍**
