@echo off
echo ====================================================
echo VetEvidence X (Twitter) Setup
echo ====================================================
echo.
echo Launching browser for manual X.com login...
echo Please log in with the PawMedical account.
echo.
echo When you reach the timeline, return here and press Enter.
echo.

python auto_post_x.py --setup

echo.
echo Setup Complete! Press any key to exit.
pause >nul
