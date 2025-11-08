@echo off
echo ========================================
echo COMPREHENSIVE TRAINING DATA GENERATOR
echo ========================================
echo.
echo This will add 1100+ diverse training samples:
echo   - 400+ Negative sentiments
echo   - 400+ Positive sentiments
echo   - 300+ Neutral statements
echo.
echo Categories include:
echo   ^> Product reviews, service experiences
echo   ^> Emotions, relationships, work
echo   ^> Entertainment, travel, healthcare
echo   ^> Technology, education, finance
echo   ^> And much more...
echo.
pause
echo.

REM Activate virtual environment and run generator
call venv\Scripts\activate.bat
python generate_large_dataset.py

echo.
echo ========================================
echo TRAINING THE MODEL
echo ========================================
echo.
echo Now that you have 1000+ samples, let's train the model!
echo.
pause

REM Automatically run training after dataset generation
python scripts\train_initial_model.py

echo.
echo ========================================
echo COMPLETE!
echo ========================================
echo.
echo Your model is now trained on 1000+ diverse samples!
echo.
echo Next steps:
echo 1. Restart your API server (if running)
echo 2. Test with challenging phrases like:
echo    - "Tragic events have unfolded"
echo    - "Absolutely thrilled with results"
echo    - "The meeting is on Tuesday"
echo.
echo The model should now be much more accurate!
echo.
pause
