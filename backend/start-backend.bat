@echo off
rem Backend: set secret key and start FastAPI on port 8080
cd /d "%~dp0"

set "FRONTEND_BUILD_DIR=%~dp0..\static"
set "WEBUI_SECRET_KEY=b8e1c94f6d2a7e3f0c5d8a1b4e7f9c2d"
set "PYTHON=C:\Users\22382\AppData\Local\conda\conda\envs\openwebui\python.exe"

echo Starting backend at http://localhost:8080
"%PYTHON%" -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080 --reload

echo.
echo Backend exited. Check the messages above if something went wrong.
pause
