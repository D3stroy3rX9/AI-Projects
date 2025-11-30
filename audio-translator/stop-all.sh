#!/bin/bash

# Audio Auto-Translator - Stop All Services Script

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🛑 Audio Auto-Translator - Stopping All Services"
echo "================================================"
echo ""

# Stop PostgreSQL
echo "📦 Stopping PostgreSQL..."
docker compose down
echo "  ✅ PostgreSQL stopped"

# Kill backend if running
echo "🐍 Stopping Backend (if running)..."
if lsof -ti:8000 > /dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo "  ✅ Backend stopped"
else
    echo "  ℹ️  Backend was not running"
fi

# Kill frontend if running
echo "⚛️  Stopping Frontend (if running)..."
if lsof -ti:3000 > /dev/null 2>&1; then
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo "  ✅ Frontend stopped"
else
    echo "  ℹ️  Frontend was not running"
fi

echo ""
echo "✅ All services stopped"
