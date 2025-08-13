#!/bin/bash

# =============================================================================
# ASIA.fr Travel Agent - Refactored System Startup
# =============================================================================
# This script starts the refactored application with unified configuration
# Frontend: Symfony on port 8001
# Backend: FastAPI on port 8000
# =============================================================================

echo "🚀 Starting ASIA.fr Travel Agent (Refactored System)"
echo "=================================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if Symfony CLI is available
if ! command -v symfony &> /dev/null; then
    echo "❌ Symfony CLI is not installed or not in PATH"
    echo "Install from: https://symfony.com/download"
    exit 1
fi

# Kill existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "python.*api.server" 2>/dev/null || true
symfony server:stop 2>/dev/null || true
sleep 2

# Check if ports are available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 8000 is already in use"
    exit 1
fi

if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 8001 is already in use"
    exit 1
fi

# Start Python API backend
echo "🐍 Starting Python API backend on port 8000..."
cd cftravel_py
python -m api.server &
PYTHON_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/status > /dev/null; then
    echo "❌ Backend failed to start on port 8000"
    kill $PYTHON_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend is running on http://localhost:8000"

# Start Symfony frontend
echo "🔄 Starting Symfony frontend on port 8001..."
symfony server:start -d --port=8001

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 3

# Check if frontend is running
if ! curl -s http://localhost:8001 > /dev/null; then
    echo "❌ Frontend failed to start on port 8001"
    kill $PYTHON_PID 2>/dev/null || true
    symfony server:stop 2>/dev/null || true
    exit 1
fi

echo "✅ Frontend is running on http://localhost:8001"

# Test unified configuration
echo "🔧 Testing unified configuration..."
if curl -s http://localhost:8001/api/config > /dev/null; then
    echo "✅ Unified configuration is working"
else
    echo "⚠️ Unified configuration test failed"
fi

# Test model management
echo "🤖 Testing model management..."
if curl -s http://localhost:8000/models > /dev/null; then
    echo "✅ Model management is working"
else
    echo "⚠️ Model management test failed"
fi

echo ""
echo "🎉 ASIA.fr Travel Agent is ready!"
echo "=================================="
echo "Frontend: http://localhost:8001"
echo "Backend:  http://localhost:8000"
echo "API Config: http://localhost:8001/api/config"
echo "Models: http://localhost:8000/models"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop
trap 'echo ""; echo "🛑 Stopping servers..."; kill $PYTHON_PID 2>/dev/null || true; symfony server:stop 2>/dev/null || true; echo "✅ All servers stopped"; exit 0' INT

# Keep script running
wait $PYTHON_PID 