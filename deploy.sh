#!/bin/bash

# =============================================================================
# ASIA.fr Travel Agent - Production Deployment Script
# =============================================================================

echo "🚀 Starting ASIA.fr Travel Agent deployment..."

# Check if we're in the right directory
if [ ! -f "composer.json" ]; then
    echo "❌ Error: composer.json not found. Please run this script from the project root."
    exit 1
fi

# Set production environment
echo "📦 Setting up production environment..."
cp env.production .env

# Add and commit changes
echo "📝 Adding changes to Git..."
git add .

echo "💾 Committing changes..."
git commit -m "🚀 Production deployment: $(date)"

# Push to production
echo "🚀 Pushing to production server..."
git push -u iagent master

echo "✅ Deployment completed!"
echo "🌐 Production URLs:"
echo "   - Main: https://asia-iagent.cftravel.net"
echo "   - Alias: https://ovg-iagent.cftravel.net"
echo ""
echo "⚠️  IMPORTANT: Make sure to update the .env file on the production server with your actual API keys!" 