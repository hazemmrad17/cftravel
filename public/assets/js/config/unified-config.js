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
        loadPromise: null, // Add promise to track loading

        /**
         * Load configuration from PHP backend
         */
        async loadConfig() {
            // If already loaded, return immediately
            if (this.loaded && this.config) {
                return this.config;
            }
            
            // If already loading, wait for the existing promise
            if (this.loading && this.loadPromise) {
                return await this.loadPromise;
            }
    
            this.loading = true;
            this.loadPromise = this._loadConfigInternal();
            
            try {
                const result = await this.loadPromise;
                return result;
            } finally {
                this.loading = false;
                this.loadPromise = null;
            }
        },
    
        /**
         * Internal loading method
         */
        async _loadConfigInternal() {
            try {
                const response = await fetch('/api/config');
                if (response.ok) {
                    this.config = await response.json();
                    console.log('✅ Configuration loaded from PHP backend');
                    console.log('🔧 PHP config API base_url:', this.config?.api?.base_url);
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.warn('⚠️ Failed to load config from PHP, using fallback:', error.message);
                this.config = this.loadFallbackConfig();
            }
    
            this.loaded = true;
            return this.config;
        },

        /**
         * Load fallback configuration based on current environment
         */
        loadFallbackConfig() {
            console.log('🔧 Loading fallback configuration...');
            
            const hostname = window.location.hostname;
            const port = window.location.port;
            const search = window.location.search;
            
            // Debug info
            const debug = {
                hostname,
                port,
                isLocal: hostname === 'localhost' || hostname === '127.0.0.1',
                forceProxy: search.includes('proxy=true') || port === '8001',
                isLocalDevelopment: hostname === 'localhost' || hostname === '127.0.0.1',
                search
            };
            
            console.log('🔧 Fallback config debug:', debug);
            
            // Determine if we should force proxy usage
            const forceProxy = debug.forceProxy;
            const isLocalDevelopment = debug.isLocalDevelopment;
            
            // Set API base URL based on environment
            let apiBaseUrl;
            if (forceProxy || !isLocalDevelopment) {
                apiBaseUrl = '/api';
            } else {
                apiBaseUrl = 'http://localhost:8000';
            }
            
            console.log('🔧 Fallback config API base_url:', apiBaseUrl);
            
            return {
                environment: isLocalDevelopment ? 'local' : 'production',
                debug: isLocalDevelopment,
                servers: {
                    frontend: {
                        host: hostname,
                        port: port || (isLocalDevelopment ? '8001' : '443'),
                        url: `${window.location.protocol}//${hostname}${port ? ':' + port : ''}`
                    },
                    backend: {
                        host: isLocalDevelopment ? 'localhost' : hostname,
                        port: isLocalDevelopment ? '8000' : '8000',
                        url: isLocalDevelopment ? 'http://localhost:8000' : `https://${hostname}:8000`
                    }
                },
                api: {
                    base_url: apiBaseUrl,
                    endpoints: {
                        chat_stream: '/chat/stream',
                        memory_clear: '/memory/clear',
                        offers: '/offers',
                        backup_models: '/backup-models'
                    }
                },
                cors: {
                    allowed_origins: ['*'],
                    allowed_methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                    allowed_headers: ['*']
                },
                ai: {
                    provider: 'groq',
                    api_key: '', // Remove process.env reference
                    models: {
                        reasoning: {
                            name: 'moonshotai/kimi-k2-instruct',
                            temperature: 0.1,
                            max_tokens: 1024,
                            enabled: true
                        },
                        generation: {
                            name: 'moonshotai/kimi-k2-instruct',
                            temperature: 0.7,
                            max_tokens: 2048,
                            enabled: true
                        },
                        matcher: {
                            name: 'moonshotai/kimi-k2-instruct',
                            temperature: 0.1,
                            max_tokens: 512,
                            enabled: true
                        },
                        extractor: {
                            name: 'moonshotai/kimi-k2-instruct',
                            temperature: 0.1,
                            max_tokens: 1024,
                            enabled: true
                        }
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