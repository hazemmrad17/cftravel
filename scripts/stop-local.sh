#!/bin/bash

# ASIA.fr Travel Agent - Stop Local Development Script

echo "🛑 Stopping ASIA.fr Travel Agent (Local Development)"

# Stop Symfony server
echo "🔄 Stopping Symfony frontend..."
symfony server:stop 2>/dev/null || true

# Stop Python backend
echo "🐍 Stopping Python API backend..."
pkill -f "python.*api.server" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

echo "✅ All servers stopped!" 