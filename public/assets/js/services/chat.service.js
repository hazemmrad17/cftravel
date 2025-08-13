/**
 * Chat Service for ASIA.fr Agent Frontend
 */

// Get services from global scope (only if not already defined)
if (typeof API_CONFIG === 'undefined') {
    const API_CONFIG = window.API_CONFIG || {
        ENDPOINTS: {
            CHAT: '/chat',
            CHAT_STREAM: '/chat/stream',
            WELCOME: '/welcome',
            MEMORY_CLEAR: '/chat/memory/clear'
        }
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
if (typeof ChatService === 'undefined') {
    class ChatService {
        constructor() {
            this.endpoints = window.API_CONFIG.ENDPOINTS;
        }

        /**
         * Get API service instance
         */
        getApiService() {
            return window.apiService;
        }

        /**
         * Send a chat message
         */
        async sendMessage(message, conversationId = null, userId = "1") {
            try {
                window.Logger.info(`💬 Sending message: ${message.substring(0, 50)}...`);
                
                const data = {
                    message: message,
                    conversation_id: conversationId,
                    user_id: userId
                };

                const apiService = this.getApiService();
                const response = await apiService.post(this.endpoints.CHAT, data);
                
                window.Logger.info(`✅ Message sent successfully`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to send message: ${error.message}`);
                throw error;
            }
        }

        /**
         * Send a streaming chat message
         */
        async sendStreamingMessage(message, conversationId = null, userId = "1", callbacks = {}) {
            try {
                window.Logger.info(`🌊 Sending streaming message: ${message.substring(0, 50)}...`);
                
                const data = {
                    message: message,
                    conversation_id: conversationId,
                    user_id: userId
                };

                const apiService = this.getApiService();
                await apiService.createStreamingRequest(
                    this.endpoints.CHAT_STREAM,
                    data,
                    callbacks.onChunk,
                    callbacks.onComplete,
                    callbacks.onError
                );
                
            } catch (error) {
                window.Logger.error(`❌ Failed to send streaming message: ${error.message}`);
                throw error;
            }
        }

        /**
         * Get welcome message
         */
        async getWelcomeMessage() {
            try {
                window.Logger.info(`👋 Getting welcome message`);
                
                const apiService = this.getApiService();
                const response = await apiService.get(this.endpoints.WELCOME);
                
                window.Logger.info(`✅ Welcome message received`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to get welcome message: ${error.message}`);
                throw error;
            }
        }

        /**
         * Clear conversation memory
         */
        async clearMemory() {
            try {
                window.Logger.info(`🧹 Clearing conversation memory`);
                
                const apiService = this.getApiService();
                const response = await apiService.post(this.endpoints.MEMORY_CLEAR, {});
                
                window.Logger.info(`✅ Memory cleared successfully`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to clear memory: ${error.message}`);
                throw error;
            }
        }

        /**
         * Get user preferences
         */
        async getPreferences() {
            try {
                window.Logger.info(`⚙️ Getting user preferences`);
                
                const apiService = this.getApiService();
                const response = await apiService.get(this.endpoints.PREFERENCES);
                
                window.Logger.info(`✅ Preferences retrieved`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to get preferences: ${error.message}`);
                throw error;
            }
        }

        /**
         * Update user preference
         */
        async updatePreference(key, value) {
            try {
                window.Logger.info(`⚙️ Updating preference: ${key} = ${value}`);
                
                const data = { key, value };
                const apiService = this.getApiService();
                const response = await apiService.post(this.endpoints.PREFERENCES, data);
                
                window.Logger.info(`✅ Preference updated successfully`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to update preference: ${error.message}`);
                throw error;
            }
        }

        /**
         * Clear all preferences
         */
        async clearPreferences() {
            try {
                window.Logger.info(`🗑️ Clearing all preferences`);
                
                const apiService = this.getApiService();
                const response = await apiService.delete(this.endpoints.PREFERENCES);
                
                window.Logger.info(`✅ Preferences cleared successfully`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to clear preferences: ${error.message}`);
                throw error;
            }
        }

        /**
         * Get conversation history
         */
        async getConversationHistory(conversationId) {
            try {
                window.Logger.info(`📜 Getting conversation history: ${conversationId}`);
                
                const apiService = this.getApiService();
                const response = await apiService.get(`/conversation/${conversationId}/history`);
                
                window.Logger.info(`✅ Conversation history retrieved`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to get conversation history: ${error.message}`);
                throw error;
            }
        }

        /**
         * Create a new conversation
         */
        async createConversation(userId = "1") {
            try {
                window.Logger.info(`🆕 Creating new conversation`);
                
                const data = { user_id: userId };
                const apiService = this.getApiService();
                const response = await apiService.post('/conversation', data);
                
                window.Logger.info(`✅ New conversation created: ${response.conversation_id}`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to create conversation: ${error.message}`);
                throw error;
            }
        }

        /**
         * Delete a conversation
         */
        async deleteConversation(conversationId) {
            try {
                window.Logger.info(`🗑️ Deleting conversation: ${conversationId}`);
                
                const apiService = this.getApiService();
                const response = await apiService.delete(`/conversation/${conversationId}`);
                
                window.Logger.info(`✅ Conversation deleted successfully`);
                return response;
                
            } catch (error) {
                window.Logger.error(`❌ Failed to delete conversation: ${error.message}`);
                throw error;
            }
        }
    }

    // Create and export singleton instance
    const chatService = new ChatService();

    // Make available globally
    window.chatService = chatService;
    window.ChatService = ChatService;
} 