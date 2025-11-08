@echo off
echo ========================================
echo Seeding Database
echo ========================================

REM Activate virtual environment and run seed.py
call venv\Scripts\activate.bat
python seed.py

echo.
pause
