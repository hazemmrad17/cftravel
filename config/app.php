<?php

/**
 * UNIFIED APPLICATION CONFIGURATION
 * =================================
 * This is the SINGLE source of truth for the entire application.
 * All settings are centralized here and accessed by PHP, Python, and JavaScript.
 * 
 * USAGE:
 * - PHP: Use ConfigurationService to access these settings
 * - Python: Use unified_config.py to parse this file
 * - JavaScript: Use unified-config.js to fetch from /api/config
 */

return [
    // =============================================================================
    // ENVIRONMENT & DEBUG
    // =============================================================================
    'environment' => $_ENV['ENVIRONMENT'] ?? 'local', // local, staging, production
    'debug' => ($_ENV['ENVIRONMENT'] ?? 'local') !== 'production',
    
    // =============================================================================
    // SERVER CONFIGURATION (Ports & URLs)
    // =============================================================================
    'servers' => [
        'frontend' => [
            'host' => '127.0.0.1',
            'port' => 8001,
            'url' => 'http://127.0.0.1:8001'
        ],
        'backend' => [
            'host' => '0.0.0.0',
            'port' => 8000,
            'url' => 'http://localhost:8000'
        ]
    ],
    
    // =============================================================================
    // API CONFIGURATION
    // =============================================================================
    'api' => [
        'base_url' => ($_ENV['ENVIRONMENT'] === 'production' || 
                      (isset($_SERVER['HTTP_HOST']) && strpos($_SERVER['HTTP_HOST'], ':8001') !== false)) 
                      ? '/api' : 'http://localhost:8000',
        'timeout' => 30,
        'retry_attempts' => 3,
        'endpoints' => [
            'chat' => '/chat',
            'chat_stream' => '/chat/stream',
            'memory_clear' => '/memory/clear',
            'chat_memory_clear' => '/chat/memory/clear',
            'status' => '/status',
            'welcome' => '/welcome',
            'preferences' => '/preferences',
            'models' => '/models',
            'models_switches' => '/models/switches',
            'models_switch' => '/models/switch/{model_type}',
            'models_validation' => '/models/validation'
        ]
    ],
    
    // =============================================================================
    // CORS CONFIGURATION
    // =============================================================================
    'cors' => [
        'allowed_origins' => [
            'https://ovg-iagent.cftravel.net',
            'https://iagent.cftravel.net',
            'http://ovg-iagent.cftravel.net',
            'http://iagent.cftravel.net',
            'http://localhost:8000',
            'http://localhost:8001',
            'http://localhost:8002',
            'http://localhost:3000',
            'http://127.0.0.1:8000',
            'http://127.0.0.1:8001',
            'http://127.0.0.1:8002',
            'http://127.0.0.1:3000'
        ],
        'allowed_methods' => ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allowed_headers' => ['*'],
        'allow_credentials' => true
    ],
    
    // =============================================================================
    // AI MODEL MANAGEMENT (Electricity Switch Style)
    // =============================================================================
    'ai' => [
        // API Provider Configuration
        'provider' => 'groq',
        'api_key' => $_ENV['GROQ_API_KEY'] ?? null, // Load from environment variable
        
        // =============================================================================
        // MODEL SWITCHES (Like Electricity Switches - ON/OFF)
        // =============================================================================
        'model_switches' => [
            'use_reasoning_model' => true,      // Controls orchestration and decision making
            'use_generation_model' => true,     // Controls response generation
            'use_matcher_model' => true,        // Controls offer matching
            'use_extractor_model' => true,      // Controls preference extraction
            'use_embedding_model' => true       // Controls semantic search
        ],
        
        // =============================================================================
        // MODEL CONFIGURATIONS
        // =============================================================================
        'models' => [
            'reasoning' => [
                'name' => 'moonshotai/kimi-k2-instruct',
                'temperature' => 0.7,
                'max_tokens' => 4000,
                'top_p' => 0.9,
                'enabled' => true
            ],
            'generation' => [
                'name' => 'moonshotai/kimi-k2-instruct',
                'temperature' => 0.8,
                'max_tokens' => 4000,
                'top_p' => 0.9,
                'enabled' => true
            ],
            'matcher' => [
                'name' => 'moonshotai/kimi-k2-instruct',
                'temperature' => 0.3,
                'max_tokens' => 2000,
                'top_p' => 0.8,
                'enabled' => true
            ],
            'extractor' => [
                'name' => 'moonshotai/kimi-k2-instruct',
                'temperature' => 0.1,
                'max_tokens' => 2000,
                'top_p' => 0.7,
                'enabled' => true
            ]
        ],
        
        // =============================================================================
        // AVAILABLE MODELS (Model Library)
        // =============================================================================
        'available_models' => [
            // Fast Models (Quick responses)
            'fast' => [
                'llama-3.1-8b-instant' => 'Fast, good for simple tasks',
                'mixtral-8x7b-32768' => 'Fast, good reasoning',
                'gemma-7b-it' => 'Fast, good for generation'
            ],
            // Balanced Models (Good performance/speed ratio)
            'balanced' => [
                'llama-3.1-70b-versatile' => 'Balanced performance (RECOMMENDED)',
                'mixtral-8x7b-32768' => 'Good all-rounder',
                'qwen2.5-32b-instruct' => 'Strong reasoning'
            ],
            // Powerful Models (Best quality, slower)
            'powerful' => [
                'llama-3.1-405b-reasoning' => 'Best reasoning, slow',
                'qwen2.5-72b-instruct' => 'Very powerful, slower',
                'mixtral-8x7b-32768' => 'Good balance'
            ],
            // French-Optimized Models
            'french' => [
                'llama-3.1-70b-versatile' => 'Good French understanding',
                'llama-3.1-8b-instant' => 'Fast French responses',
                'mixtral-8x7b-32768' => 'Good French support'
            ]
        ],
        
        // =============================================================================
        // EMBEDDING MODEL CONFIGURATION
        // =============================================================================
        'embedding_model' => [
            'name' => 'all-MiniLM-L6-v2',
            'enabled' => true,
            'max_length' => 512,
            'similarity_threshold' => 0.7
        ],
        
        // =============================================================================
        // MEMORY CONFIGURATION
        // =============================================================================
        'memory' => [
            'enabled' => true,
            'max_conversations' => 100,
            'max_messages_per_conversation' => 50,
            'retention_days' => 30
        ],
        
        // =============================================================================
        // SEMANTIC SEARCH CONFIGURATION
        // =============================================================================
        'semantic_search' => [
            'enabled' => true,
            'index_path' => './cftravel_py/data/semantic_index',
            'max_results' => 5,
            'similarity_threshold' => 0.7
        ]
    ]
];