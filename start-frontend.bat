@echo off
rem Frontend: start Vite dev server on port 5173 (fast mode, skips pyodide download)
cd /d "%~dp0"

if not exist "node_modules\.bin\vite.cmd" (
    echo.
    echo [ERROR] Frontend dependencies not found (node_modules missing or incomplete).
    echo Please run the following command in this folder first:
    echo     npm install
    echo If Node.js is newer than 22, use: npm install --engine-strict=false
    echo.
    pause
    exit /b 1
)

echo Starting frontend at http://localhost:5173
npm run dev:fast

echo.
echo Frontend exited. Check the messages above if something went wrong.
pause
