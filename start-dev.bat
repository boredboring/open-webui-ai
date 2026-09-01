@echo off
rem Start backend and frontend in separate windows
cd /d "%~dp0"

start "Open WebUI Backend" "%~dp0backend\start-backend.bat"
start "Open WebUI Frontend" "%~dp0start-frontend.bat"

echo.
echo Backend : http://localhost:8080
echo Frontend: http://localhost:5173
echo.
echo Once both windows are ready, open http://localhost:5173 in your browser.
pause
