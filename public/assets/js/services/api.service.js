/**
 * API Service for ASIA.fr Agent Frontend
 */

// Get configuration from global scope (only if not already defined)
if (typeof API_CONFIG === 'undefined') {
    const API_CONFIG = window.API_CONFIG || {
        BASE_URL: 'http://localhost:8000',
        TIMEOUT: 30000,
        RETRY_ATTEMPTS: 3
    };
    window.API_CONFIG = API_CONFIG;
}

// Get logger from global scope (only if not already defined)
if (typeof Logger === 'undefined') {
    const Logger = window.Logger || {
        debug: console.debug,
        info: console.info,
        warn: console.warn,
        error: console.error
    };
    window.Logger = Logger;
}

// Only create the class if it doesn't exist
if (typeof ApiService === 'undefined') {
    class ApiService {
        constructor() {
            this.baseUrl = window.API_CONFIG.BASE_URL;
            this.timeout = window.API_CONFIG.TIMEOUT;
            this.retryAttempts = window.API_CONFIG.RETRY_ATTEMPTS;
        }

        /**
         * Make a generic API request
         */
        async request(endpoint, options = {}) {
            const url = `${this.baseUrl}${endpoint}`;
            const config = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                timeout: this.timeout,
                ...options
            };

            try {
                window.Logger.debug(`🌐 API Request: ${config.method} ${url}`);
                
                const response = await fetch(url, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                window.Logger.debug(`✅ API Response:`, data);
                
                return data;
                
            } catch (error) {
                window.Logger.error(`❌ API Error: ${error.message}`);
                throw error;
            }
        }

        /**
         * Make a POST request
         */
        async post(endpoint, data, options = {}) {
            return this.request(endpoint, {
                method: 'POST',
                body: JSON.stringify(data),
                ...options
            });
        }

        /**
         * Make a GET request
         */
        async get(endpoint, options = {}) {
            return this.request(endpoint, {
                method: 'GET',
                ...options
            });
        }

        /**
         * Make a DELETE request
         */
        async delete(endpoint, options = {}) {
            return this.request(endpoint, {
                method: 'DELETE',
                ...options
            });
        }

        /**
         * Make a request with retry logic
         */
        async requestWithRetry(endpoint, options = {}, maxRetries = this.retryAttempts) {
            let lastError;
            
            for (let attempt = 1; attempt <= maxRetries; attempt++) {
                try {
                    return await this.request(endpoint, options);
                } catch (error) {
                    lastError = error;
                    window.Logger.warn(`⚠️ API attempt ${attempt} failed: ${error.message}`);
                    
                    if (attempt < maxRetries) {
                        // Wait before retrying (exponential backoff)
                        const delay = Math.pow(2, attempt) * 1000;
                        await new Promise(resolve => setTimeout(resolve, delay));
                    }
                }
            }
            
            throw lastError;
        }

        /**
         * Create a streaming request
         */
        async createStreamingRequest(endpoint, data, onChunk, onComplete, onError) {
            const url = `${this.baseUrl}${endpoint}`;
            
            try {
                window.Logger.debug(`🌊 Starting streaming request: ${url}`);
                
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) {
                        window.Logger.debug('✅ Streaming completed');
                        onComplete?.();
                        break;
                    }

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                onChunk?.(data);
                            } catch (parseError) {
                                window.Logger.warn(`⚠️ Failed to parse streaming chunk: ${parseError.message}`);
                            }
                        }
                    }
                }
                
            } catch (error) {
                window.Logger.error(`❌ Streaming error: ${error.message}`);
                onError?.(error);
            }
        }

        /**
         * Health check
         */
        async healthCheck() {
            return this.get('/health');
        }

        /**
         * Get API status
         */
        async getStatus() {
            return this.get('/status');
        }
    }

    // Create and export singleton instance
    const apiService = new ApiService();

    // Make available globally
    window.apiService = apiService;
    window.ApiService = ApiService;
} 