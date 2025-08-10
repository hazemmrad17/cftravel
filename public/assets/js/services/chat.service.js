/**
 * Chat Service for ASIA.fr Agent Frontend
 */

import { apiService } from './api.service.js';
import { API_CONFIG } from '../core/config.js';
import { Logger } from '../core/utils.js';

class ChatService {
    constructor() {
        this.endpoints = API_CONFIG.ENDPOINTS;
    }

    /**
     * Send a chat message
     */
    async sendMessage(message, conversationId = null, userId = "1") {
        try {
            Logger.info(`💬 Sending message: ${message.substring(0, 50)}...`);
            
            const data = {
                message: message,
                conversation_id: conversationId,
                user_id: userId
            };

            const response = await apiService.post(this.endpoints.CHAT, data);
            
            Logger.info(`✅ Message sent successfully`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to send message: ${error.message}`);
            throw error;
        }
    }

    /**
     * Send a streaming chat message
     */
    async sendStreamingMessage(message, conversationId = null, userId = "1", callbacks = {}) {
        try {
            Logger.info(`🌊 Sending streaming message: ${message.substring(0, 50)}...`);
            
            const data = {
                message: message,
                conversation_id: conversationId,
                user_id: userId
            };

            await apiService.createStreamingRequest(
                this.endpoints.CHAT_STREAM,
                data,
                callbacks.onChunk,
                callbacks.onComplete,
                callbacks.onError
            );
            
        } catch (error) {
            Logger.error(`❌ Failed to send streaming message: ${error.message}`);
            throw error;
        }
    }

    /**
     * Get welcome message
     */
    async getWelcomeMessage() {
        try {
            Logger.info(`👋 Getting welcome message`);
            
            const response = await apiService.get(this.endpoints.WELCOME);
            
            Logger.info(`✅ Welcome message received`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to get welcome message: ${error.message}`);
            throw error;
        }
    }

    /**
     * Clear conversation memory
     */
    async clearMemory() {
        try {
            Logger.info(`🧹 Clearing conversation memory`);
            
            const response = await apiService.post(this.endpoints.MEMORY_CLEAR, {});
            
            Logger.info(`✅ Memory cleared successfully`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to clear memory: ${error.message}`);
            throw error;
        }
    }

    /**
     * Get user preferences
     */
    async getPreferences() {
        try {
            Logger.info(`⚙️ Getting user preferences`);
            
            const response = await apiService.get(this.endpoints.PREFERENCES);
            
            Logger.info(`✅ Preferences retrieved`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to get preferences: ${error.message}`);
            throw error;
        }
    }

    /**
     * Update user preference
     */
    async updatePreference(key, value) {
        try {
            Logger.info(`⚙️ Updating preference: ${key} = ${value}`);
            
            const data = { key, value };
            const response = await apiService.post(this.endpoints.PREFERENCES, data);
            
            Logger.info(`✅ Preference updated successfully`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to update preference: ${error.message}`);
            throw error;
        }
    }

    /**
     * Clear all preferences
     */
    async clearPreferences() {
        try {
            Logger.info(`🗑️ Clearing all preferences`);
            
            const response = await apiService.delete(this.endpoints.PREFERENCES);
            
            Logger.info(`✅ Preferences cleared successfully`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to clear preferences: ${error.message}`);
            throw error;
        }
    }

    /**
     * Get conversation history
     */
    async getConversationHistory(conversationId) {
        try {
            Logger.info(`📜 Getting conversation history: ${conversationId}`);
            
            const response = await apiService.get(`/conversation/${conversationId}/history`);
            
            Logger.info(`✅ Conversation history retrieved`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to get conversation history: ${error.message}`);
            throw error;
        }
    }

    /**
     * Create a new conversation
     */
    async createConversation(userId = "1") {
        try {
            Logger.info(`🆕 Creating new conversation`);
            
            const data = { user_id: userId };
            const response = await apiService.post('/conversation', data);
            
            Logger.info(`✅ New conversation created: ${response.conversation_id}`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to create conversation: ${error.message}`);
            throw error;
        }
    }

    /**
     * Delete a conversation
     */
    async deleteConversation(conversationId) {
        try {
            Logger.info(`🗑️ Deleting conversation: ${conversationId}`);
            
            const response = await apiService.delete(`/conversation/${conversationId}`);
            
            Logger.info(`✅ Conversation deleted successfully`);
            return response;
            
        } catch (error) {
            Logger.error(`❌ Failed to delete conversation: ${error.message}`);
            throw error;
        }
    }
}

// Export singleton instance
export const chatService = new ChatService(); 