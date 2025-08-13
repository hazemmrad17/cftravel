<?php

namespace App\Service;

use Psr\Log\LoggerInterface;

/**
 * UNIFIED CONFIGURATION SERVICE
 * ============================
 * Provides centralized access to application configuration.
 * This is the single source of truth for all application settings.
 */
class ConfigurationService
{
    private array $config;
    private LoggerInterface $logger;

    public function __construct(string $configFile, LoggerInterface $logger)
    {
        $this->logger = $logger;
        $this->loadConfig($configFile);
    }

    /**
     * Load configuration from the unified config file
     */
    private function loadConfig(string $configFile): void
    {
        try {
            if (!file_exists($configFile)) {
                throw new \RuntimeException("Configuration file not found: {$configFile}");
            }

            $this->config = require $configFile;
            $this->logger->info('Unified configuration loaded successfully');
            
            // Log key configuration details
            $this->logger->info('Configuration Summary:', [
                'environment' => $this->getEnvironment(),
                'debug' => $this->isDebug(),
                'frontend_url' => $this->getServer('frontend')['url'] ?? 'N/A',
                'backend_url' => $this->getServer('backend')['url'] ?? 'N/A',
                'ai_provider' => $this->getAi()['provider'] ?? 'N/A'
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Failed to load configuration: ' . $e->getMessage());
            throw new \RuntimeException('Configuration loading failed: ' . $e->getMessage());
        }
    }

    /**
     * Get entire configuration
     */
    public function getAll(): array
    {
        return $this->config;
    }

    /**
     * Get a specific configuration section
     */
    public function get(string $section): array
    {
        return $this->config[$section] ?? [];
    }

    /**
     * Get a specific configuration value
     */
    public function getValue(string $section, string $key, $default = null)
    {
        return $this->config[$section][$key] ?? $default;
    }

    /**
     * Get server configuration
     */
    public function getServer(string $server): array
    {
        return $this->config['servers'][$server] ?? [];
    }

    /**
     * Get API configuration
     */
    public function getApi(): array
    {
        return $this->config['api'] ?? [];
    }

    /**
     * Get API endpoint URL
     */
    public function getApiEndpoint(string $endpoint): string
    {
        $apiConfig = $this->getApi();
        $baseUrl = $apiConfig['base_url'] ?? '';
        $endpointPath = $apiConfig['endpoints'][$endpoint] ?? $endpoint;
        
        return rtrim($baseUrl, '/') . '/' . ltrim($endpointPath, '/');
    }

    /**
     * Get CORS configuration
     */
    public function getCors(): array
    {
        return $this->config['cors'] ?? [];
    }

    /**
     * Get AI configuration
     */
    public function getAi(): array
    {
        return $this->config['ai'] ?? [];
    }

    /**
     * Get environment
     */
    public function getEnvironment(): string
    {
        return $this->config['environment'] ?? 'local';
    }

    /**
     * Check if debug mode is enabled
     */
    public function isDebug(): bool
    {
        return $this->config['debug'] ?? false;
    }

    /**
     * Check if running in production
     */
    public function isProduction(): bool
    {
        return $this->getEnvironment() === 'production';
    }

    /**
     * Check if running locally
     */
    public function isLocal(): bool
    {
        return $this->getEnvironment() === 'local';
    }

    /**
     * Get database configuration
     */
    public function getDatabase(): array
    {
        return $this->config['database'] ?? [];
    }

    /**
     * Get data paths configuration
     */
    public function getData(): array
    {
        return $this->config['data'] ?? [];
    }

    /**
     * Get language configuration
     */
    public function getLanguage(): array
    {
        return $this->config['language'] ?? [];
    }

    /**
     * Get UI configuration
     */
    public function getUi(): array
    {
        return $this->config['ui'] ?? [];
    }

    /**
     * Get chat configuration
     */
    public function getChat(): array
    {
        return $this->config['chat'] ?? [];
    }

    /**
     * Log current configuration for debugging
     */
    public function logConfig(): void
    {
        $this->logger->info('=== UNIFIED CONFIGURATION ===');
        $this->logger->info('Environment: ' . $this->getEnvironment());
        $this->logger->info('Debug Mode: ' . ($this->isDebug() ? 'true' : 'false'));
        
        $servers = $this->get('servers');
        $this->logger->info('Frontend: ' . ($servers['frontend']['url'] ?? 'N/A'));
        $this->logger->info('Backend: ' . ($servers['backend']['url'] ?? 'N/A'));
        
        $aiConfig = $this->get('ai');
        $this->logger->info('AI Provider: ' . ($aiConfig['provider'] ?? 'N/A'));
        $this->logger->info('API Key Set: ' . (!empty($aiConfig['api_key']) ? 'Yes' : 'No'));
        
        $modelSwitches = $aiConfig['model_switches'] ?? [];
        $this->logger->info('Model Switches:');
        foreach ($modelSwitches as $model => $enabled) {
            $this->logger->info('  ' . $model . ': ' . ($enabled ? 'ON' : 'OFF'));
        }
        
        $this->logger->info('=== END CONFIGURATION ===');
    }
} 