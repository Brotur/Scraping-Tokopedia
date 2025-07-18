@echo off
echo Starting Tokopedia AI Consultant System
echo ======================================

echo.
echo Checking Python environment...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Testing system components...
python test_ai_integration.py

echo.
echo Starting APIs...
echo.
echo Starting Scraper API on port 8000...
start "Scraper API" cmd /k "python tokopedia_scraper_api.py"

echo Waiting for Scraper API to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting AI Consultant API on port 8001...
start "AI Consultant API" cmd /k "python ai_consultant_api.py"

echo Waiting for AI Consultant API to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting Frontend on port 3000...
start "Frontend" cmd /k "python -m http.server 3000 --directory frontend"

echo.
echo System is starting up...
echo.
echo APIs will be available at:
echo   Scraper API: http://localhost:8000
echo   AI Consultant: http://localhost:8001
echo   Frontend: http://localhost:3000
echo.
echo Press any key to open the frontend in your browser...
pause > nul

start http://localhost:3000

echo.
echo System is now running!
echo Press any key to exit...
pause
