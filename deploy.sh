#!/bin/bash

# CFTravel IA Agent Deployment Script
# Usage: ./deploy.sh [local|production]

set -e

ENVIRONMENT=${1:-local}

echo "🚀 Starting deployment for environment: $ENVIRONMENT"

if [ "$ENVIRONMENT" = "production" ]; then
    echo "📦 Deploying to production server..."
    
    # Copy production environment file
    if [ -f "env.production" ]; then
        cp env.production .env
        echo "✅ Production environment file copied"
    else
        echo "❌ env.production file not found"
        exit 1
    fi
    
    # Add and commit the .env file
    git add .env
    git commit -m "Update production environment configuration" || true
    
    # Push to production
    echo "📤 Pushing to production server..."
    git push iagent master
    
    echo "✅ Deployment completed!"
    echo "🌐 Production URL: https://asia-iagent.cftravel.net"
    echo "🔗 Alias URL: https://ovg-iagent.cftravel.net"
    
elif [ "$ENVIRONMENT" = "local" ]; then
    echo "🔧 Setting up local environment..."
    
    # Copy local environment file
    if [ -f "env.local" ]; then
        cp env.local .env
        echo "✅ Local environment configured"
    else
        echo "❌ env.local file not found"
        exit 1
    fi
    
    echo "✅ Local setup completed!"
    echo "🚀 Run: python cftravel_py/api/server.py"
    
else
    echo "❌ Invalid environment. Use 'local' or 'production'"
    exit 1
fi 