# Audio Auto-Translator - Quick Start

Get up and running in 5 minutes!

---

## 🚀 Automated Setup (Recommended)

### Linux/macOS:
```bash
cd /home/user/AI-Projects/audio-translator
./setup.sh
```

### Windows:
```cmd
cd C:\path\to\audio-translator
setup.bat
```

**That's it!** The script will:
- ✅ Check all prerequisites
- ✅ Set up environment variables
- ✅ Start PostgreSQL database
- ✅ Install all dependencies
- ✅ Run database migrations
- ✅ Download Whisper models

---

## ▶️ Start the Application

### Terminal 1 - Backend:
```bash
cd apps/api
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

uvicorn main:app --reload
```

### Terminal 2 - Frontend:
```bash
cd apps/web
pnpm dev
```

---

## 🌐 Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🧪 Quick Test

1. Open http://localhost:3000
2. Click "Record" button
3. Say: "Hello, how are you?"
4. Click "Stop Recording"
5. Wait for translation to appear
6. Success! ✅

---

## 🛠️ Manual Setup (If Script Fails)

### 1. Start PostgreSQL:
```bash
docker compose up -d
```

### 2. Create Environment Files:
```bash
# Backend
cp apps/api/.env.example apps/api/.env

# Frontend
cp apps/web/.env.local.example apps/web/.env.local
```

### 3. Setup Backend:
```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
python -c "import whisper; whisper.load_model('base')"
```

### 4. Setup Frontend:
```bash
cd apps/web
pnpm install
```

### 5. Start Services:
```bash
# Terminal 1
cd apps/api
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2
cd apps/web
pnpm dev
```

---

## ⚠️ Common Issues

### Docker not starting?
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop
```

### Port 5432 already in use?
```bash
# Stop existing PostgreSQL
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # macOS

# Or change port in docker-compose.yml to 5433:5432
```

### Backend errors?
```bash
# Check if PostgreSQL is running
docker compose ps

# Check if venv is activated (you should see (venv) in prompt)
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend errors?
```bash
# Reinstall dependencies
cd apps/web
rm -rf node_modules
pnpm install
```

---

## 📚 Full Documentation

For detailed information, see:
- `SETUP_GUIDE.md` - Complete setup instructions with troubleshooting
- `README.md` - Project overview and features
- `DEPLOYMENT.md` - Production deployment guide
- `API_DOCUMENTATION.md` - API reference

---

## 🎯 Next Steps

1. ✅ Complete setup
2. ✅ Test basic translation
3. 📖 Read `README.md` for all features
4. 🧪 Try conversation mode: http://localhost:3000/conversation
5. 📜 View history: http://localhost:3000/history
6. ⚙️ Adjust settings: http://localhost:3000/settings
7. 🌙 Toggle dark mode
8. 🚀 Deploy to production (see `DEPLOYMENT.md`)

---

**Need help?** Check `SETUP_GUIDE.md` for detailed troubleshooting!

**Happy translating! 🎤🌍**
