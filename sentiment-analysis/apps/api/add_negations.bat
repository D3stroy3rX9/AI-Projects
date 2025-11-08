@echo off
echo ========================================
echo ADDING NEGATION TRAINING DATA
echo ========================================
echo.
echo This will add ~2000 specialized samples
echo to improve handling of:
echo   - Negations (not bad, can't complain)
echo   - Subtle expressions
echo   - Edge cases
echo.

call venv\Scripts\activate.bat
python add_negation_training.py

pause

echo.
echo ========================================
echo RETRAINING MODEL
echo ========================================
echo.

python scripts\train_initial_model.py

echo.
echo ========================================
echo COMPLETE!
echo ========================================
echo.
echo Test again with: "This product is not bad"
echo Should now classify as POSITIVE
echo.

pause
