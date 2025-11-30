#!/bin/bash

# Audio Auto-Translator - Start Frontend Script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🎤 Audio Auto-Translator - Starting Frontend"
echo "============================================"
echo ""

cd apps/web

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not found!"
    echo "   Please run ./setup.sh first or run: pnpm install"
    exit 1
fi

echo "Frontend will start at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

pnpm dev
