#!/bin/bash

# ASIA.fr Travel Agent - Local Development Startup Script
# This script starts both the Symfony frontend and Python backend

echo "🚀 Starting ASIA.fr Travel Agent (Local Development)"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if Symfony CLI is installed
if ! command -v symfony &> /dev/null; then
    echo "❌ Symfony CLI is not installed or not in PATH"
    exit 1
fi

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
pkill -f "python.*api.server" 2>/dev/null || true
symfony server:stop 2>/dev/null || true

# Start Python backend
echo "🐍 Starting Python API backend on port 8000..."
cd cftravel_py
python -m api.server &
PYTHON_PID=$!
cd ..

# Wait a moment for Python to start
sleep 3

# Start Symfony frontend
echo "🔄 Starting Symfony frontend on port 8001..."
symfony server:start -d --port=8001

# Wait a moment for Symfony to start
sleep 3

echo ""
echo "✅ ASIA.fr Travel Agent is now running!"
echo ""
echo "🌐 Frontend: http://localhost:8001"
echo "🔧 Backend:  http://localhost:8000"
echo ""
echo "📝 To stop the servers:"
echo "   - Press Ctrl+C to stop this script"
echo "   - Or run: ./scripts/stop-local.sh"
echo ""

# Wait for user to stop
wait $PYTHON_PID 