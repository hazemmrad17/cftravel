@echo off

REM ASIA.fr Travel Agent - Local Development Startup Script (Windows)
REM This script starts both the Symfony frontend and Python backend

echo 🚀 Starting ASIA.fr Travel Agent (Local Development)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Symfony CLI is installed
symfony --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Symfony CLI is not installed or not in PATH
    pause
    exit /b 1
)

REM Kill any existing processes on our ports
echo 🧹 Cleaning up existing processes...
taskkill /f /im python.exe >nul 2>&1
symfony server:stop >nul 2>&1

REM Start Python backend
echo 🐍 Starting Python API backend on port 8000...
cd cftravel_py
start "Python API" python -m api.server
cd ..

REM Wait a moment for Python to start
timeout /t 3 /nobreak >nul

REM Start Symfony frontend
echo 🔄 Starting Symfony frontend on port 8001...
symfony server:start -d --port=8001

REM Wait a moment for Symfony to start
timeout /t 3 /nobreak >nul

echo.
echo ✅ ASIA.fr Travel Agent is now running!
echo.
echo 🌐 Frontend: http://localhost:8001
echo 🔧 Backend:  http://localhost:8000
echo.
echo 📝 To stop the servers:
echo    - Run: scripts\stop-local.bat
echo    - Or close this window
echo.

pause 