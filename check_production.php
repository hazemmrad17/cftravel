<?php
/**
 * Production Environment Checker
 * Run this on your production server to verify configuration
 */

echo "🔍 ASIA.fr Agent - Production Environment Check\n";
echo "==============================================\n\n";

// Check environment variables
echo "📋 Environment Variables:\n";
echo "ENVIRONMENT: " . ($_ENV['ENVIRONMENT'] ?? 'NOT SET') . "\n";
echo "DEBUG: " . ($_ENV['DEBUG'] ?? 'NOT SET') . "\n";
echo "APP_ENV: " . ($_ENV['APP_ENV'] ?? 'NOT SET') . "\n";
echo "GROQ_API_KEY: " . (isset($_ENV['GROQ_API_KEY']) ? 'SET' : 'NOT SET') . "\n\n";

// Check server variables
echo "🌐 Server Information:\n";
echo "HTTP_HOST: " . ($_SERVER['HTTP_HOST'] ?? 'NOT SET') . "\n";
echo "SERVER_NAME: " . ($_SERVER['SERVER_NAME'] ?? 'NOT SET') . "\n";
echo "REQUEST_URI: " . ($_SERVER['REQUEST_URI'] ?? 'NOT SET') . "\n\n";

// Load configuration
$config = require __DIR__ . '/config/app.php';

echo "⚙️ Configuration:\n";
echo "Environment: " . $config['environment'] . "\n";
echo "Debug: " . ($config['debug'] ? 'true' : 'false') . "\n";
echo "API Base URL: " . $config['api']['base_url'] . "\n";
echo "Frontend URL: " . $config['servers']['frontend']['url'] . "\n";
echo "Backend URL: " . $config['servers']['backend']['url'] . "\n\n";

// Check if .env file exists
$envFile = __DIR__ . '/.env';
echo "📁 .env File:\n";
if (file_exists($envFile)) {
    echo "✅ .env file exists\n";
    $envContent = file_get_contents($envFile);
    if (strpos($envContent, 'ENVIRONMENT=production') !== false) {
        echo "✅ ENVIRONMENT=production found in .env\n";
    } else {
        echo "❌ ENVIRONMENT=production NOT found in .env\n";
    }
} else {
    echo "❌ .env file does not exist\n";
    echo "💡 Create it from env.production template\n";
}

echo "\n🔧 Recommendations:\n";
if (!isset($_ENV['ENVIRONMENT']) || $_ENV['ENVIRONMENT'] !== 'production') {
    echo "❌ Set ENVIRONMENT=production in .env file\n";
}
if ($config['api']['base_url'] !== '/api') {
    echo "❌ API base_url should be '/api' for production\n";
}
if ($config['debug']) {
    echo "❌ Debug should be false for production\n";
}

echo "\n✅ Check complete!\n";
?> 