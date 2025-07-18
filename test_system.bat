@echo off
echo Testing Tokopedia AI Consultant System
echo ======================================

echo.
echo 1. Testing server health...
python test_health.py

echo.
echo 2. Testing data mapping...
python test_mapping.py

echo.
echo 3. Testing complete!
echo.
echo To start the system:
echo   1. python tokopedia_scraper_api.py
echo   2. python ai_consultant_api.py  
echo   3. python -m http.server 3000 --directory frontend
echo.
pause
