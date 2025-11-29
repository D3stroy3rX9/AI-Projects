#!/bin/bash

# Audio Auto-Translator - Automated Setup Script
# This script automates the setup process for local development

set -e  # Exit on error

echo "🎤 Audio Auto-Translator - Setup Script"
echo "========================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Step 1: Check Prerequisites
echo "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check Python
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "  ✅ Python $PYTHON_VERSION"
else
    echo "  ❌ Python not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  ✅ Node.js $NODE_VERSION"
else
    echo "  ❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check pnpm
if command -v pnpm &> /dev/null; then
    PNPM_VERSION=$(pnpm --version)
    echo "  ✅ pnpm $PNPM_VERSION"
else
    echo "  ❌ pnpm not found. Installing..."
    npm install -g pnpm
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    echo "  ✅ Docker $DOCKER_VERSION"
else
    echo "  ⚠️  Docker not found. You'll need to install PostgreSQL manually."
fi

# Check ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo "  ✅ ffmpeg installed"
else
    echo "  ⚠️  ffmpeg not found. Installing it is recommended."
    echo "     macOS: brew install ffmpeg"
    echo "     Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "     Windows: Download from https://ffmpeg.org/"
fi

echo ""

# Step 2: Set Up Environment Variables
echo "${BLUE}Step 2: Setting up environment variables...${NC}"

# Backend .env
if [ ! -f "apps/api/.env" ]; then
    cp apps/api/.env.example apps/api/.env
    echo "  ✅ Created apps/api/.env"
else
    echo "  ℹ️  apps/api/.env already exists (skipping)"
fi

# Frontend .env.local
if [ ! -f "apps/web/.env.local" ]; then
    cp apps/web/.env.local.example apps/web/.env.local
    echo "  ✅ Created apps/web/.env.local"
else
    echo "  ℹ️  apps/web/.env.local already exists (skipping)"
fi

echo ""

# Step 3: Start PostgreSQL
echo "${BLUE}Step 3: Starting PostgreSQL database...${NC}"

if command -v docker &> /dev/null; then
    # Check if docker compose or docker-compose is available
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        echo "  ❌ Docker Compose not found"
        exit 1
    fi

    # Start PostgreSQL
    $DOCKER_COMPOSE up -d
    echo "  ✅ PostgreSQL started"

    # Wait for PostgreSQL to be ready
    echo "  ⏳ Waiting for PostgreSQL to be ready..."
    sleep 5

    # Check if PostgreSQL is running
    if $DOCKER_COMPOSE ps | grep -q "audio-translator-db"; then
        echo "  ✅ PostgreSQL is running"
    else
        echo "  ❌ PostgreSQL failed to start. Check logs: $DOCKER_COMPOSE logs"
        exit 1
    fi
else
    echo "  ⚠️  Docker not available. Please install PostgreSQL manually."
    echo "     Update DATABASE_URL in apps/api/.env to point to your PostgreSQL instance."
fi

echo ""

# Step 4: Set Up Backend
echo "${BLUE}Step 4: Setting up backend (Python)...${NC}"

cd apps/api

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "  📦 Creating virtual environment..."
    python -m venv venv
    echo "  ✅ Virtual environment created"
else
    echo "  ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo "  🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "  📦 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  ✅ Python dependencies installed"

# Run database migrations
echo "  🗄️  Running database migrations..."
alembic upgrade head
echo "  ✅ Database migrations complete"

# Download Whisper model
if [ ! -f "$HOME/.cache/whisper/base.pt" ]; then
    echo "  📥 Downloading Whisper model (74MB, this may take a minute)..."
    python -c "import whisper; whisper.load_model('base')"
    echo "  ✅ Whisper model downloaded"
else
    echo "  ℹ️  Whisper model already downloaded"
fi

cd ../..
echo ""

# Step 5: Set Up Frontend
echo "${BLUE}Step 5: Setting up frontend (Next.js)...${NC}"

cd apps/web

# Install dependencies
echo "  📦 Installing Node.js dependencies (this may take a few minutes)..."
pnpm install --silent
echo "  ✅ Node.js dependencies installed"

cd ../..
echo ""

# Step 6: Summary
echo "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "========================================"
echo "🚀 How to Start the Application"
echo "========================================"
echo ""
echo "${YELLOW}Terminal 1 - Backend (FastAPI):${NC}"
echo "  cd $PROJECT_ROOT/apps/api"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "  source venv/Scripts/activate"
else
    echo "  source venv/bin/activate"
fi
echo "  uvicorn main:app --reload"
echo ""
echo "${YELLOW}Terminal 2 - Frontend (Next.js):${NC}"
echo "  cd $PROJECT_ROOT/apps/web"
echo "  pnpm dev"
echo ""
echo "========================================"
echo "📍 Application URLs"
echo "========================================"
echo "  Frontend:    ${GREEN}http://localhost:3000${NC}"
echo "  Backend API: ${GREEN}http://localhost:8000${NC}"
echo "  API Docs:    ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "========================================"
echo "📚 Documentation"
echo "========================================"
echo "  Setup Guide:    SETUP_GUIDE.md"
echo "  README:         README.md"
echo "  Deployment:     DEPLOYMENT.md"
echo "  API Docs:       API_DOCUMENTATION.md"
echo ""
echo "Happy translating! 🎤🌍"
