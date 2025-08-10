/**
 * API Service for ASIA.fr Agent Frontend
 */

import { API_CONFIG } from '../core/config.js';
import { Logger } from '../core/utils.js';

class ApiService {
    constructor() {
        this.baseUrl = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
        this.retryAttempts = API_CONFIG.RETRY_ATTEMPTS;
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
            Logger.debug(`🌐 API Request: ${config.method} ${url}`);
            
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            Logger.debug(`✅ API Response:`, data);
            
            return data;
            
        } catch (error) {
            Logger.error(`❌ API Error: ${error.message}`);
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
                Logger.warn(`⚠️ API attempt ${attempt} failed: ${error.message}`);
                
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
            Logger.debug(`🌊 Starting streaming request: ${url}`);
            
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
                    Logger.debug('✅ Streaming completed');
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
                            Logger.warn(`⚠️ Failed to parse streaming chunk: ${parseError.message}`);
                        }
                    }
                }
            }
            
        } catch (error) {
            Logger.error(`❌ Streaming error: ${error.message}`);
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

// Export singleton instance
export const apiService = new ApiService(); 