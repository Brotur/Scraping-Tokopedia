@echo off
echo 🚀 Starting Enhanced AI Shopping Consultant System
echo ===============================================
echo 🎯 NEW FEATURES:
echo    - Professional confidence display
echo    - Comprehensive review analysis
echo    - Enhanced AI insights
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
echo 🤖 Starting Enhanced AI Consultant API (Port 8001)...
start "AI Consultant API" cmd /k "cd /d %~dp0 && python ai_consultant_api.py"

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Open frontend
echo 🌐 Opening Enhanced Frontend...
start "" "frontend\index.html"

echo.
echo ✅ Enhanced System Started Successfully!
echo.
echo 📊 Services Running:
echo    - Scraper API: http://localhost:8000
echo    - Enhanced AI Consultant API: http://localhost:8001
echo    - Professional Frontend: file:///frontend/index.html
echo.
echo 🎯 NEW FEATURES AVAILABLE:
echo    - Professional confidence display with animations
echo    - Comprehensive review analysis (all reviews considered)
echo    - Enhanced AI insights with theme extraction
echo    - Risk assessment based on negative reviews
echo    - Satisfaction level calculation
echo    - Consistency analysis
echo.
echo 🧪 Available Tests:
echo    - python test_enhanced_confidence.py  (NEW - Test enhanced features)
echo    - python test_structure_compatibility.py
echo    - python test_full_structure.py
echo    - python test_ai_integration.py
echo.
echo 📚 Documentation:
echo    - ENHANCED_CONFIDENCE_DOCUMENTATION.md (NEW)
echo    - AI_CONSULTANT_ENHANCED.md
echo    - README.md
echo.
echo 🎨 UI/UX Improvements:
echo    - Animated confidence display
echo    - Color-coded confidence levels
echo    - Professional metrics display
echo    - Enhanced error handling
echo    - Responsive design
echo.
echo Press any key to exit...
pause > nul
