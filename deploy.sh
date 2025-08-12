#!/bin/bash

# Deployment script for CFTravel AI Agent
echo "🚀 Starting deployment to production..."

# 1. Check if we're in the right directory
if [ ! -f "ecosystem.config.js" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# 2. Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ Error: PM2 is not installed. Please install it first:"
    echo "   npm install -g pm2"
    exit 1
fi

# 3. Stop existing PM2 process
echo "🛑 Stopping existing PM2 process..."
pm2 stop cftravel-api 2>/dev/null || true
pm2 delete cftravel-api 2>/dev/null || true

# 4. Start the new process
echo "🚀 Starting new PM2 process..."
pm2 start ecosystem.config.js

# 5. Save PM2 configuration
echo "💾 Saving PM2 configuration..."
pm2 save

# 6. Check status
echo "📊 Checking PM2 status..."
pm2 status

# 7. Show logs
echo "📋 Recent logs:"
pm2 logs cftravel-api --lines 10

echo "✅ Deployment completed!"
echo "🌐 Your API should now be available at: https://ovg-iagent.cftravel.net"
echo "📝 To monitor logs: pm2 logs cftravel-api"
echo "🔄 To restart: pm2 restart cftravel-api" 