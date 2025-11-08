@echo off
echo ========================================
echo 10,000 SAMPLE DATASET GENERATOR
echo ========================================
echo.
echo This will add ~8,600 samples to reach 10K total
echo Expected accuracy improvement: 70-75%% -^> 75-80%%
echo.

call venv\Scripts\activate.bat
python generate_10k_dataset.py

pause

echo.
echo ========================================
echo TRAINING MODEL ON 10K SAMPLES
echo ========================================
echo This may take 5-10 minutes...
echo.

python scripts\train_initial_model.py

echo.
echo ========================================
echo COMPLETE!
echo ========================================
echo Model trained on ~10,000 samples
echo Check the accuracy metrics above
echo.

pause
