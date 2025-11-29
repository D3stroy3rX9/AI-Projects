@echo off
REM Audio Auto-Translator - Automated Setup Script (Windows)
REM This script automates the setup process for local development

echo.
echo Audio Auto-Translator - Setup Script (Windows)
echo ========================================
echo.

REM Get project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo Project root: %PROJECT_ROOT%
echo.

REM Step 1: Check Prerequisites
echo Step 1: Checking prerequisites...

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo   [OK] Python %PYTHON_VERSION%
) else (
    echo   [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
    echo   [OK] Node.js %NODE_VERSION%
) else (
    echo   [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

REM Check pnpm
where pnpm >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=1" %%i in ('pnpm --version') do set PNPM_VERSION=%%i
    echo   [OK] pnpm %PNPM_VERSION%
) else (
    echo   [WARN] pnpm not found. Installing...
    call npm install -g pnpm
)

REM Check Docker
where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
    echo   [OK] Docker %DOCKER_VERSION%
) else (
    echo   [WARN] Docker not found. You'll need to install PostgreSQL manually.
)

REM Check ffmpeg
where ffmpeg >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] ffmpeg installed
) else (
    echo   [WARN] ffmpeg not found. Installing it is recommended.
    echo         Windows: Download from https://ffmpeg.org/
)

echo.

REM Step 2: Set Up Environment Variables
echo Step 2: Setting up environment variables...

REM Backend .env
if not exist "apps\api\.env" (
    copy "apps\api\.env.example" "apps\api\.env" >nul
    echo   [OK] Created apps\api\.env
) else (
    echo   [INFO] apps\api\.env already exists (skipping)
)

REM Frontend .env.local
if not exist "apps\web\.env.local" (
    copy "apps\web\.env.local.example" "apps\web\.env.local" >nul
    echo   [OK] Created apps\web\.env.local
) else (
    echo   [INFO] apps\web\.env.local already exists (skipping)
)

echo.

REM Step 3: Start PostgreSQL
echo Step 3: Starting PostgreSQL database...

where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    REM Try docker compose first, then docker-compose
    docker compose version >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        docker compose up -d
    ) else (
        where docker-compose >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            docker-compose up -d
        ) else (
            echo   [ERROR] Docker Compose not found
            pause
            exit /b 1
        )
    )
    echo   [OK] PostgreSQL started

    REM Wait for PostgreSQL to be ready
    echo   Waiting for PostgreSQL to be ready...
    timeout /t 5 /nobreak >nul
    echo   [OK] PostgreSQL should be ready

) else (
    echo   [WARN] Docker not available. Please install PostgreSQL manually.
    echo          Update DATABASE_URL in apps\api\.env to point to your PostgreSQL instance.
)

echo.

REM Step 4: Set Up Backend
echo Step 4: Setting up backend (Python)...

cd apps\api

REM Create virtual environment
if not exist "venv" (
    echo   Creating virtual environment...
    python -m venv venv
    echo   [OK] Virtual environment created
) else (
    echo   [INFO] Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo   Activating virtual environment...
call venv\Scripts\activate.bat

echo   Installing Python dependencies...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo   [OK] Python dependencies installed

REM Run database migrations
echo   Running database migrations...
alembic upgrade head
echo   [OK] Database migrations complete

REM Download Whisper model
if not exist "%USERPROFILE%\.cache\whisper\base.pt" (
    echo   Downloading Whisper model (74MB, this may take a minute)...
    python -c "import whisper; whisper.load_model('base')"
    echo   [OK] Whisper model downloaded
) else (
    echo   [INFO] Whisper model already downloaded
)

cd ..\..
echo.

REM Step 5: Set Up Frontend
echo Step 5: Setting up frontend (Next.js)...

cd apps\web

echo   Installing Node.js dependencies (this may take a few minutes)...
call pnpm install --silent
echo   [OK] Node.js dependencies installed

cd ..\..
echo.

REM Step 6: Summary
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo ========================================
echo How to Start the Application
echo ========================================
echo.
echo Terminal 1 - Backend (FastAPI):
echo   cd %PROJECT_ROOT%apps\api
echo   venv\Scripts\activate
echo   uvicorn main:app --reload
echo.
echo Terminal 2 - Frontend (Next.js):
echo   cd %PROJECT_ROOT%apps\web
echo   pnpm dev
echo.
echo ========================================
echo Application URLs
echo ========================================
echo   Frontend:    http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo.
echo ========================================
echo Documentation
echo ========================================
echo   Setup Guide:    SETUP_GUIDE.md
echo   README:         README.md
echo   Deployment:     DEPLOYMENT.md
echo   API Docs:       API_DOCUMENTATION.md
echo.
echo Happy translating!
echo.

pause
