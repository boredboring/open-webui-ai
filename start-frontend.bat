@echo off
rem Frontend: start Vite dev server on port 5173 (fast mode, skips pyodide download)
cd /d "%~dp0"

echo Starting frontend at http://localhost:5173
npm run dev:fast

echo.
echo Frontend exited. Check the messages above if something went wrong.
pause
