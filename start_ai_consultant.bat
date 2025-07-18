@echo off
echo 🤖 AI Shopping Consultant - Quick Start Script
echo =============================================
echo.

echo ✅ Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak ditemukan. Install Python terlebih dahulu.
    pause
    exit /b 1
)

echo ✅ Installing dependencies...
pip install -r requirements.txt
pip install -r requirements_ai.txt

echo.
echo 📋 Setup Instructions:
echo 1. Edit file .env dan masukkan Gemini API Key Anda
echo 2. Dapatkan API Key dari: https://makersuite.google.com/app/apikey
echo 3. Jalankan kedua API server dalam terminal terpisah
echo.

echo 🚀 Starting servers...
echo Opening new terminals for each server...

start "Scraper API" cmd /k "echo Starting Scraper API (Port 8000)... && python tokopedia_scraper_api.py"
timeout /t 3 >nul

start "AI API" cmd /k "echo Starting AI API (Port 8001)... && python ai_consultant_api.py"
timeout /t 3 >nul

echo.
echo 🌐 Opening frontend...
start "" "frontend\index.html"

echo.
echo ✅ Setup complete!
echo 📊 APIs running on:
echo    - Scraper API: http://localhost:8000
echo    - AI API: http://localhost:8001
echo 🌐 Frontend: frontend/index.html
echo.
echo 🧪 Run tests with: python test_ai_consultant.py
echo.
pause
