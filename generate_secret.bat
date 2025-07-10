@echo off
echo 🔐 PrBot_Pay Secret Key Generator
echo ========================================
echo.

python generate_secret.py --count 1 --type urlsafe

echo.
echo Press any key to exit...
pause >nul 