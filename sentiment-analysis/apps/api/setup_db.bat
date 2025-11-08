@echo off
REM Get Poetry virtual environment path and run create_tables.py

echo Finding Poetry virtual environment...
for /f "delims=" %%i in ('poetry env info --path') do set VENV_PATH=%%i

echo Using Python from: %VENV_PATH%
"%VENV_PATH%\Scripts\python.exe" create_tables.py

pause
