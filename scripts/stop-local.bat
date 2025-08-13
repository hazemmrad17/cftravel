@echo off

REM ASIA.fr Travel Agent - Stop Local Development Script (Windows)

echo 🛑 Stopping ASIA.fr Travel Agent (Local Development)

REM Stop Symfony server
echo 🔄 Stopping Symfony frontend...
symfony server:stop >nul 2>&1

REM Stop Python backend
echo 🐍 Stopping Python API backend...
taskkill /f /im python.exe >nul 2>&1

REM Wait a moment for processes to stop
timeout /t 2 /nobreak >nul

echo ✅ All servers stopped!
pause 