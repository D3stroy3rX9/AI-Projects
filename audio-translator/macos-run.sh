#!/bin/bash

# Audio Auto-Translator - macOS All-In-One Setup & Run Script
# Just run this once and everything will be set up and started automatically.

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "🎤 Audio Auto-Translator - macOS Setup & Run"
echo "============================================="
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# ─── Step 1: Homebrew ────────────────────────────────────────────────────────
echo "${BLUE}[1/7] Checking Homebrew...${NC}"
if ! command -v brew &>/dev/null; then
    echo "  Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for Apple Silicon
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi
echo "  ✅ Homebrew $(brew --version | head -1)"

# ─── Step 2: System Dependencies ─────────────────────────────────────────────
echo "${BLUE}[2/7] Installing system dependencies...${NC}"

brew_install() {
    if ! command -v "$1" &>/dev/null; then
        echo "  Installing $1..."
        brew install "$2"
    else
        echo "  ✅ $1 already installed"
    fi
}

brew_install python3 python@3.11
brew_install node node
brew_install ffmpeg ffmpeg

if ! command -v pnpm &>/dev/null; then
    echo "  Installing pnpm..."
    npm install -g pnpm
else
    echo "  ✅ pnpm already installed"
fi

# ─── Step 3: Docker ──────────────────────────────────────────────────────────
echo "${BLUE}[3/7] Checking Docker...${NC}"
if ! command -v docker &>/dev/null; then
    echo ""
    echo "  ${RED}⚠️  Docker is not installed.${NC}"
    echo "  Please install Docker Desktop for Mac:"
    echo "  👉 https://www.docker.com/products/docker-desktop/"
    echo ""
    echo "  After installing, open Docker Desktop and come back to run this script again."
    echo ""
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &>/dev/null; then
    echo "  ${YELLOW}⚠️  Docker Desktop is not running. Attempting to start...${NC}"
    open -a Docker
    echo "  ⏳ Waiting for Docker to start (up to 60 seconds)..."
    for i in $(seq 1 30); do
        sleep 2
        if docker info &>/dev/null; then
            echo "  ✅ Docker is running"
            break
        fi
        if [ "$i" -eq 30 ]; then
            echo "  ${RED}❌ Docker didn't start in time. Please open Docker Desktop manually and re-run this script.${NC}"
            exit 1
        fi
    done
else
    echo "  ✅ Docker is running"
fi

# ─── Step 4: Environment Variables ───────────────────────────────────────────
echo "${BLUE}[4/7] Setting up environment variables...${NC}"

if [ ! -f "apps/api/.env" ]; then
    cp apps/api/.env.example apps/api/.env
    echo "  ✅ Created apps/api/.env"
else
    echo "  ✅ apps/api/.env already exists"
fi

if [ ! -f "apps/web/.env.local" ]; then
    cp apps/web/.env.local.example apps/web/.env.local
    echo "  ✅ Created apps/web/.env.local"
else
    echo "  ✅ apps/web/.env.local already exists"
fi

# ─── Step 5: PostgreSQL ───────────────────────────────────────────────────────
echo "${BLUE}[5/7] Starting PostgreSQL...${NC}"
if docker compose ps 2>/dev/null | grep -q "audio-translator-db.*Up"; then
    echo "  ✅ PostgreSQL already running"
else
    docker compose up -d
    echo "  ⏳ Waiting for PostgreSQL to be ready..."
    for i in $(seq 1 15); do
        sleep 2
        if docker compose exec -T postgres pg_isready -U translator -d audio_translator &>/dev/null; then
            echo "  ✅ PostgreSQL is ready"
            break
        fi
        if [ "$i" -eq 15 ]; then
            echo "  ${YELLOW}⚠️  PostgreSQL may not be fully ready yet, continuing anyway...${NC}"
        fi
    done
fi

# ─── Step 6: Backend Setup ────────────────────────────────────────────────────
echo "${BLUE}[6/7] Setting up Python backend...${NC}"

cd apps/api

if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "  Installing Python dependencies (this may take a few minutes)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  ✅ Python dependencies installed"

echo "  Running database migrations..."
alembic upgrade head
echo "  ✅ Migrations done"

if [ ! -f "$HOME/.cache/whisper/base.pt" ]; then
    echo "  Downloading Whisper model (~74MB)..."
    python3 -c "import whisper; whisper.load_model('base')" 2>&1 | tail -1
    echo "  ✅ Whisper model ready"
else
    echo "  ✅ Whisper model already downloaded"
fi

deactivate
cd ../..

# ─── Step 7: Frontend Setup ───────────────────────────────────────────────────
echo "${BLUE}[7/7] Setting up frontend...${NC}"
cd apps/web
pnpm install --silent
echo "  ✅ Frontend dependencies installed"
cd ../..

# ─── Launch ───────────────────────────────────────────────────────────────────
echo ""
echo "${GREEN}✅ Setup complete! Launching the app...${NC}"
echo ""
echo "  Backend  → http://localhost:8000"
echo "  Frontend → http://localhost:3000"
echo "  API Docs → http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop everything."
echo ""

# Start backend in background
cd apps/api
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ../..

# Wait for backend to be ready
echo "  ⏳ Waiting for backend to start..."
for i in $(seq 1 15); do
    sleep 1
    if curl -s http://localhost:8000 &>/dev/null; then
        echo "  ✅ Backend is up"
        break
    fi
done

# Open browser
sleep 1
echo "  🌐 Opening http://localhost:3000 in your browser..."
open http://localhost:3000 &

# Start frontend in foreground
cd apps/web
pnpm dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null; docker compose down" EXIT
