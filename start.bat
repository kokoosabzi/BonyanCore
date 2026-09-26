@echo off
setlocal
title BonyanCore - Local Launcher
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
  py -m venv venv
  if errorlevel 1 (echo Failed to create venv.& pause& exit /b 1)
)

call "venv\Scripts\activate.bat"
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (pause& exit /b 1)

echo Starting BonyanCore...
echo API:     http://127.0.0.1:8000/
echo Swagger: http://127.0.0.1:8000/docs
echo Health:  http://127.0.0.1:8000/health
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause
endlocal