@echo off
rem Backend: activate the shared conda environment and start FastAPI on port 8080
cd /d "%~dp0"

set "FRONTEND_BUILD_DIR=%~dp0..\static"
set "COURSE_CORPUS_DIR=%~dp0..\data\corpus"
set "WEBUI_SECRET_KEY=b8e1c94f6d2a7e3f0c5d8a1b4e7f9c2d"

rem Activate the shared conda environment (see README for setup)
call conda activate openwebui
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to activate conda environment "openwebui".
    echo See README.md environment setup section for details.
    echo.
    pause
    exit /b 1
)

echo Starting backend at http://localhost:8080
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080 --reload

echo.
echo Backend exited. Check the messages above if something went wrong.
pause
