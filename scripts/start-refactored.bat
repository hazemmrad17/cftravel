@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM ASIA.fr Travel Agent - Refactored System Startup (Windows)
REM =============================================================================
REM This script starts the refactored application with unified configuration
REM Frontend: Symfony on port 8001
REM Backend: FastAPI on port 8000
REM =============================================================================

echo 🚀 Starting ASIA.fr Travel Agent (Refactored System)
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Symfony CLI is available
symfony --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Symfony CLI is not installed or not in PATH
    echo Install from: https://symfony.com/download
    pause
    exit /b 1
)

REM Kill existing processes
echo 🧹 Cleaning up existing processes...
taskkill /F /IM python.exe 2>nul
symfony server:stop 2>nul
timeout /t 2 /nobreak >nul

REM Check if ports are available
netstat -an | findstr ":8000" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo ❌ Port 8000 is already in use
    pause
    exit /b 1
)

netstat -an | findstr ":8001" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo ❌ Port 8001 is already in use
    pause
    exit /b 1
)

REM Start Python API backend
echo 🐍 Starting Python API backend on port 8000...
cd cftravel_py
start /B python -m api.server
cd ..

REM Wait for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8000/status >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend failed to start on port 8000
    pause
    exit /b 1
)

echo ✅ Backend is running on http://localhost:8000

REM Start Symfony frontend
echo 🔄 Starting Symfony frontend on port 8001...
symfony server:start -d --port=8001

REM Wait for frontend to start
echo ⏳ Waiting for frontend to start...
timeout /t 3 /nobreak >nul

REM Check if frontend is running
curl -s http://localhost:8001 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend failed to start on port 8001
    pause
    exit /b 1
)

echo ✅ Frontend is running on http://localhost:8001

REM Test unified configuration
echo 🔧 Testing unified configuration...
curl -s http://localhost:8001/api/config >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Unified configuration test failed
) else (
    echo ✅ Unified configuration is working
)

REM Test model management
echo 🤖 Testing model management...
curl -s http://localhost:8000/models >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Model management test failed
) else (
    echo ✅ Model management is working
)

echo.
echo 🎉 ASIA.fr Travel Agent is ready!
echo ==================================
echo Frontend: http://localhost:8001
echo Backend:  http://localhost:8000
echo API Config: http://localhost:8001/api/config
echo Models: http://localhost:8000/models
echo.
echo Press any key to stop all servers
echo.

pause

REM Stop servers
echo 🛑 Stopping servers...
taskkill /F /IM python.exe 2>nul
symfony server:stop 2>nul
echo ✅ All servers stopped
pause 