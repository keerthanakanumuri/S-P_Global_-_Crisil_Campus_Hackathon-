@echo off
title FinRisk AI — Backend Server
color 0B

echo.
echo  =====================================================
echo   FinRisk AI — Real-Time Financial Risk Intelligence
echo  =====================================================
echo.

:: Move into backend folder
cd /d "%~dp0backend"

:: Create venv if it doesn't exist
if not exist "venv\" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    echo       Done.
) else (
    echo [1/3] Virtual environment already exists.
)

:: Activate venv
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install / upgrade dependencies
echo [3/3] Installing dependencies (this may take a moment on first run)...
pip install -r requirements.txt --quiet

echo.
echo  -------------------------------------------------------
echo   Backend starting at  http://127.0.0.1:8000
echo   API docs at          http://127.0.0.1:8000/docs
echo.
echo   Frontend: open  frontend\index.html  in your browser
echo  -------------------------------------------------------
echo.

:: Launch FastAPI
uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause
