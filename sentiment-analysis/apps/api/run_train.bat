@echo off
echo ========================================
echo Training ML Model
echo ========================================

REM Activate virtual environment and run training script
call venv\Scripts\activate.bat
python scripts\train_initial_model.py

echo.
pause
