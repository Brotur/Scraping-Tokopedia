@echo off
echo ==========================================
echo  Sentiment Visualization Test Preview
echo ==========================================
echo.

echo Starting Python HTTP Server...
echo Open browser and go to: http://localhost:8080/sentiment-test.html
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0frontend"
python -m http.server 8080

pause
