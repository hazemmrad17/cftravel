/**
 * Unified Configuration for ASIA.fr Agent Frontend
 * Loads configuration from PHP backend and provides fallback
 */

// Only create if not already defined
if (typeof UnifiedConfig === 'undefined') {
    let UnifiedConfig = {
        config: null,
        loading: false,
        loaded: false,

        /**
         * Load configuration from PHP backend
         */
        async loadConfig() {
            if (this.loading || this.loaded) {
                return this.config;
            }

            this.loading = true;

            try {
                const response = await fetch('/api/config');
                if (response.ok) {
                    this.config = await response.json();
                    console.log('✅ Configuration loaded from PHP backend');
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.warn('⚠️ Failed to load config from PHP, using fallback:', error.message);
                this.config = this.loadFallbackConfig();
            }

            this.loaded = true;
            this.loading = false;
            return this.config;
        },

        /**
         * Load configuration (alias for loadConfig)
         */
        async load() {
            return this.loadConfig();
        },

        /**
         * Load fallback configuration
         */
        loadFallbackConfig() {
            const hostname = window.location.hostname;
            const isLocal = hostname === 'localhost' || hostname === '127.0.0.1';
            
            return {
                environment: isLocal ? 'local' : 'production',
                debug: isLocal,
                servers: {
                    frontend: {
                        host: hostname,
                        port: window.location.port || (window.location.protocol === 'https:' ? '443' : '80'),
                        url: window.location.origin
                    },
                    backend: {
                        host: isLocal ? 'localhost' : 'localhost',
                        port: isLocal ? 8000 : 8000,
                        url: isLocal ? 'http://localhost:8000' : 'http://localhost:8000'
                    }
                },
                api: {
                    base_url: isLocal ? 'http://localhost:8000' : '/api',
                    timeout: 30000,
                    retry_attempts: 3,
                    endpoints: {
                        chat: '/chat',
                        chat_stream: '/chat/stream',
                        welcome: '/welcome',
                        memory_clear: '/memory/clear',
                        status: '/status',
                        health: '/health',
                        models: '/models',
                        models_switches: '/models/switches',
                        models_validation: '/models/validation',
                        models_backup_status: '/models/backup/status',
                        models_backup_test: '/models/backup/test',
                        models_backup: '/models/backup/{model_type}',
                        models_backup_test_type: '/models/backup/test/{model_type}'
                    }
                },
                cors: {
                    allowed_origins: ['http://127.0.0.1:8001', 'http://localhost:8001', 'http://127.0.0.1:8000', 'http://localhost:8000'],
                    allowed_methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                    allowed_headers: ['Content-Type', 'Authorization'],
                    allow_credentials: true
                },
                ai: {
                    provider: 'groq',
                    api_key: null,
                    models: {
                        reasoning: {
                            name: 'llama-3.1-70b-versatile',
                            temperature: 0.7,
                            max_tokens: 4000,
                            top_p: 0.9
                        },
                        generation: {
                            name: 'llama-3.1-70b-versatile',
                            temperature: 0.8,
                            max_tokens: 4000,
                            top_p: 0.9
                        },
                        matcher: {
                            name: 'llama-3.1-70b-versatile',
                            temperature: 0.3,
                            max_tokens: 2000,
                            top_p: 0.8
                        },
                        extractor: {
                            name: 'llama-3.1-70b-versatile',
                            temperature: 0.1,
                            max_tokens: 2000,
                            top_p: 0.7
                        }
                    },
                    switches: {
                        use_reasoning_model: true,
                        use_generation_model: true,
                        use_matcher_model: true,
                        use_extractor_model: true,
                        use_embedding_model: true
                    },
                    backup_models: {
                        reasoning: [
                            {
                                name: 'llama-3.1-70b-versatile',
                                temperature: 0.7,
                                max_tokens: 4000,
                                top_p: 0.9,
                                priority: 1,
                                reasoning_effort: 'high'
                            },
                            {
                                name: 'llama-3.1-8b-instant',
                                temperature: 0.7,
                                max_tokens: 2000,
                                top_p: 0.9,
                                priority: 2,
                                reasoning_effort: 'medium'
                            }
                        ],
                        generation: [
                            {
                                name: 'llama-3.1-70b-versatile',
                                temperature: 0.8,
                                max_tokens: 4000,
                                top_p: 0.9,
                                priority: 1,
                                reasoning_effort: 'high'
                            },
                            {
                                name: 'llama-3.1-8b-instant',
                                temperature: 0.8,
                                max_tokens: 2000,
                                top_p: 0.9,
                                priority: 2,
                                reasoning_effort: 'medium'
                            }
                        ],
                        matcher: [
                            {
                                name: 'llama-3.1-70b-versatile',
                                temperature: 0.3,
                                max_tokens: 2000,
                                top_p: 0.8,
                                priority: 1,
                                reasoning_effort: 'high'
                            },
                            {
                                name: 'llama-3.1-8b-instant',
                                temperature: 0.3,
                                max_tokens: 1000,
                                top_p: 0.8,
                                priority: 2,
                                reasoning_effort: 'medium'
                            }
                        ],
                        extractor: [
                            {
                                name: 'llama-3.1-70b-versatile',
                                temperature: 0.1,
                                max_tokens: 2000,
                                top_p: 0.7,
                                priority: 1,
                                reasoning_effort: 'high'
                            },
                            {
                                name: 'llama-3.1-8b-instant',
                                temperature: 0.1,
                                max_tokens: 1000,
                                top_p: 0.7,
                                priority: 2,
                                reasoning_effort: 'medium'
                            }
                        ]
                    }
                }
            };
        },

        /**
         * Get configuration value
         */
        get(key, defaultValue = null) {
            if (!this.config) {
                console.warn('⚠️ Configuration not loaded, loading now...');
                this.loadConfig();
                return defaultValue;
            }

            const keys = key.split('.');
            let value = this.config;

            for (const k of keys) {
                if (value && typeof value === 'object' && k in value) {
                    value = value[k];
                } else {
                    return defaultValue;
                }
            }

            return value;
        },

        /**
         * Get API configuration
         */
        getApi() {
            return this.get('api', this.loadFallbackConfig().api);
        },

        /**
         * Get AI configuration
         */
        getAi() {
            return this.get('ai', this.loadFallbackConfig().ai);
        },

        /**
         * Get CORS configuration
         */
        getCors() {
            return this.get('cors', this.loadFallbackConfig().cors);
        },

        /**
         * Get environment
         */
        getEnvironment() {
            return this.get('environment', 'local');
        },

        /**
         * Check if debug mode is enabled
         */
        isDebug() {
            return this.get('debug', true);
        },

        /**
         * Get frontend URL
         */
        getFrontendUrl() {
            return this.get('servers.frontend.url', 'http://127.0.0.1:8001');
        },

        /**
         * Get backend URL
         */
        getBackendUrl() {
            return this.get('servers.backend.url', 'http://localhost:8000');
        },

        /**
         * Get API base URL
         */
        getApiBaseUrl() {
            return this.get('api.base_url', 'http://localhost:8000');
        }
    };

    // Make available globally
    window.UnifiedConfig = UnifiedConfig;
    
    // Initialize global configuration objects only if they don't exist
    if (!window.API_CONFIG) {
        window.API_CONFIG = UnifiedConfig.getApi();
    }
    
    if (!window.DEBUG_CONFIG) {
        window.DEBUG_CONFIG = {
            ENABLED: UnifiedConfig.isDebug(),
            LOG_PREFIX: '[ASIA]'
        };
    }
} 