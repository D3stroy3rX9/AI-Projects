@echo off
echo ========================================
echo CHECKING DATASET COUNT
echo ========================================
echo.

call venv\Scripts\activate.bat
python check_dataset_count.py

echo.
pause
