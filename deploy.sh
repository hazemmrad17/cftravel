#!/bin/bash

# Production Deployment Script for IA Agent de voyage
echo "🚀 Starting production deployment..."

# Set production environment
echo "📋 Setting production environment..."
cp env.production .env

# Add all changes to git
echo "📦 Adding changes to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "🚀 Production deployment: $(date)"

# Push to production server
echo "🌐 Pushing to production server..."
git push -u iagent master

echo "✅ Deployment completed!"
echo "🌍 Your app should be live at: https://asia-iagent.cftravel.net"
echo "🔗 Alias: https://ovg-iagent.cftravel.net" 