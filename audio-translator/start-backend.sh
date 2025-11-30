#!/bin/bash

# Audio Auto-Translator - Start Backend Script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🎤 Audio Auto-Translator - Starting Backend"
echo "==========================================="
echo ""

# Start PostgreSQL if not running
echo "📦 Checking PostgreSQL..."
if docker compose ps | grep -q "audio-translator-db.*Up"; then
    echo "  ✅ PostgreSQL is already running"
else
    echo "  🚀 Starting PostgreSQL..."
    docker compose up -d
    echo "  ⏳ Waiting for PostgreSQL to be ready..."
    sleep 3
    echo "  ✅ PostgreSQL started"
fi

echo ""
echo "🐍 Starting Backend (FastAPI)..."
echo ""

cd apps/api

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./setup.sh first"
    exit 1
fi

# Activate venv and start server
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Backend will start at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app --reload
