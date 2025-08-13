<?php

namespace App\Service;

use Symfony\Contracts\HttpClient\HttpClientInterface;
use Psr\Log\LoggerInterface;
use Symfony\Component\HttpFoundation\Response;

/**
 * API Service
 * Handles all communication with the Python backend
 */
class ApiService
{
    private HttpClientInterface $httpClient;
    private LoggerInterface $logger;
    private ConfigurationService $config;
    
    public function __construct(
        HttpClientInterface $httpClient, 
        LoggerInterface $logger,
        ConfigurationService $config
    ) {
        $this->httpClient = $httpClient;
        $this->logger = $logger;
        $this->config = $config;
    }
    
    /**
     * Make a request to the Python API
     */
    public function request(string $method, string $endpoint, array $data = [], array $options = []): array
    {
        $url = $this->config->getApiEndpoint($endpoint);
        $timeout = $options['timeout'] ?? $this->config->getValue('api', 'timeout', 30);
        
        $this->logger->info('Making API request', [
            'method' => $method,
            'url' => $url,
            'endpoint' => $endpoint
        ]);
        
        try {
            $requestOptions = [
                'timeout' => $timeout,
                'headers' => [
                    'Content-Type' => 'application/json',
                    'Accept' => 'application/json'
                ]
            ];
            
            if (!empty($data)) {
                $requestOptions['json'] = $data;
            }
            
            $response = $this->httpClient->request($method, $url, $requestOptions);
            $responseData = $response->toArray();
            
            $this->logger->info('API request successful', [
                'status' => $response->getStatusCode(),
                'endpoint' => $endpoint
            ]);
            
            return $responseData;
            
        } catch (\Exception $e) {
            $this->logger->error('API request failed', [
                'method' => $method,
                'endpoint' => $endpoint,
                'error' => $e->getMessage()
            ]);
            
            throw $e;
        }
    }
    
    /**
     * Send a chat message
     */
    public function sendChatMessage(string $message, ?string $conversationId = null, string $userId = '1'): array
    {
        return $this->request('POST', 'chat', [
            'message' => $message,
            'conversation_id' => $conversationId,
            'user_id' => $userId
        ]);
    }
    
    /**
     * Get streaming chat response
     */
    public function getChatStream(string $message, ?string $conversationId = null, string $userId = '1'): Response
    {
        $url = $this->config->getApiEndpoint('chat_stream');
        $timeout = $this->config->getValue('api', 'timeout', 60);
        
        $this->logger->info('Making streaming API request', [
            'url' => $url,
            'conversation_id' => $conversationId
        ]);
        
        try {
            $response = $this->httpClient->request('POST', $url, [
                'json' => [
                    'message' => $message,
                    'conversation_id' => $conversationId,
                    'user_id' => $userId
                ],
                'timeout' => $timeout
            ]);
            
            $stream = $response->toStream();
            
            return new Response(
                $stream,
                $response->getStatusCode(),
                $this->getCorsHeaders([
                    'Content-Type' => 'text/event-stream',
                    'Cache-Control' => 'no-cache',
                    'Connection' => 'keep-alive',
                ])
            );
            
        } catch (\Exception $e) {
            $this->logger->error('Streaming API request failed', [
                'error' => $e->getMessage()
            ]);
            
            return new Response(
                "data: " . json_encode(['type' => 'error', 'error' => $e->getMessage()]) . "\n\n",
                500,
                $this->getCorsHeaders([
                    'Content-Type' => 'text/event-stream',
                ])
            );
        }
    }
    
    /**
     * Clear conversation memory
     */
    public function clearMemory(?string $conversationId = null): array
    {
        $data = [];
        if ($conversationId) {
            $data['conversation_id'] = $conversationId;
        }
        
        return $this->request('POST', 'memory_clear', $data);
    }
    
    /**
     * Get agent status
     */
    public function getStatus(): array
    {
        return $this->request('GET', 'status');
    }
    
    /**
     * Get welcome message
     */
    public function getWelcomeMessage(): array
    {
        return $this->request('GET', 'welcome');
    }
    
    /**
     * Get user preferences
     */
    public function getPreferences(): array
    {
        return $this->request('GET', 'preferences');
    }
    
    /**
     * Update user preference
     */
    public function updatePreference(string $key, string $value): array
    {
        return $this->request('POST', 'preferences', [
            'key' => $key,
            'value' => $value
        ]);
    }
    
    /**
     * Clear user preferences
     */
    public function clearPreferences(): array
    {
        return $this->request('DELETE', 'preferences');
    }
    
    /**
     * Get CORS headers
     */
    private function getCorsHeaders(array $additionalHeaders = []): array
    {
        $corsConfig = $this->config->getCors();
        
        $headers = [
            'Access-Control-Allow-Origin' => '*',
            'Access-Control-Allow-Methods' => implode(', ', $corsConfig['allowed_methods']),
            'Access-Control-Allow-Headers' => implode(', ', $corsConfig['allowed_headers']),
        ];
        
        if ($corsConfig['allow_credentials']) {
            $headers['Access-Control-Allow-Credentials'] = 'true';
        }
        
        return array_merge($headers, $additionalHeaders);
    }
} 