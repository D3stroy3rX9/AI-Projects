@echo off
REM Audio Auto-Translator - Start Frontend Script (Windows)

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo.
echo Audio Auto-Translator - Starting Frontend
echo ============================================
echo.

cd apps\web

REM Check if node_modules exists
if not exist "node_modules" (
    echo [ERROR] Dependencies not found!
    echo         Please run setup.bat first or run: pnpm install
    pause
    exit /b 1
)

echo Frontend will start at: http://localhost:3000
echo.
echo Press Ctrl+C to stop
echo.

pnpm dev
