#!/bin/bash

# Production Startup Script for CFTravel AI Agent
echo "🚀 Starting CFTravel AI Agent in Production Mode..."

# Navigate to the Python directory
cd /var/www/iagent.cftravel.net/cftravel_py

# Activate virtual environment
source venv/bin/activate

# Set production environment
export PORT=8000

# Start the server
echo "🔧 Starting API server on port 8000..."
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 