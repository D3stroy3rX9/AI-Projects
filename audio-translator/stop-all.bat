@echo off
REM Audio Auto-Translator - Stop All Services Script (Windows)

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo.
echo Audio Auto-Translator - Stopping All Services
echo ================================================
echo.

REM Stop PostgreSQL
echo Stopping PostgreSQL...
docker compose down
echo   [OK] PostgreSQL stopped

REM Kill backend if running
echo Stopping Backend (if running)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>nul
)
echo   [OK] Backend stopped (if it was running)

REM Kill frontend if running
echo Stopping Frontend (if running)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /F /PID %%a >nul 2>nul
)
echo   [OK] Frontend stopped (if it was running)

echo.
echo [OK] All services stopped
echo.
pause
