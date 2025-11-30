@echo off
REM Audio Auto-Translator - Start Backend Script (Windows)

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo.
echo Audio Auto-Translator - Starting Backend
echo ===========================================
echo.

REM Start PostgreSQL if not running
echo Checking PostgreSQL...
docker compose ps | findstr "audio-translator-db" | findstr "Up" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] PostgreSQL is already running
) else (
    echo   Starting PostgreSQL...
    docker compose up -d
    echo   Waiting for PostgreSQL to be ready...
    timeout /t 3 /nobreak >nul
    echo   [OK] PostgreSQL started
)

echo.
echo Starting Backend (FastAPI)...
echo.

cd apps\api

REM Check if venv exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo         Please run setup.bat first
    pause
    exit /b 1
)

REM Activate venv and start server
call venv\Scripts\activate.bat

echo Backend will start at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

uvicorn main:app --reload
