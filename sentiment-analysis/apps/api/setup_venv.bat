@echo off
echo ========================================
echo Setting up Python virtual environment
echo ========================================

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate and install dependencies
echo.
echo Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To use the environment:
echo 1. Run: venv\Scripts\activate.bat
echo 2. Then run your scripts: python create_tables.py
echo.
pause
