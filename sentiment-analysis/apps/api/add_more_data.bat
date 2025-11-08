@echo off
echo ========================================
echo Adding More Training Data
echo ========================================

REM Activate virtual environment and run script
call venv\Scripts\activate.bat
python add_training_data.py

echo.
echo After this completes, run: run_train.bat
echo to retrain the model with the new data.
echo.
pause
