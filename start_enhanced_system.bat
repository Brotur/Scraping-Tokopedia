@echo off
echo 🚀 Starting AI Shopping Consultant System (Enhanced Version)
echo ===============================================

echo.
echo 📋 Starting Services...
echo.

REM Start main scraper API
echo 🔧 Starting Main Scraper API (Port 8000)...
start "Scraper API" cmd /k "cd /d %~dp0 && python tokopedia_scraper_improved.py"

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Start AI consultant API
echo 🤖 Starting AI Consultant API (Port 8001)...
start "AI Consultant API" cmd /k "cd /d %~dp0 && python ai_consultant_api.py"

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Open frontend
echo 🌐 Opening Frontend...
start "" "frontend\index.html"

echo.
echo ✅ System Started Successfully!
echo.
echo 📊 Services Running:
echo    - Scraper API: http://localhost:8000
echo    - AI Consultant API: http://localhost:8001
echo    - Frontend: file:///frontend/index.html
echo.
echo 🧪 Available Tests:
echo    - python test_structure_compatibility.py
echo    - python test_full_structure.py
echo    - python test_ai_integration.py
echo.
echo 📚 Documentation:
echo    - AI_CONSULTANT_ENHANCED.md
echo    - README.md
echo.
echo Press any key to exit...
pause > nul
