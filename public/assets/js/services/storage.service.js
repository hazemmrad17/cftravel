/**
 * Storage Service for ASIA.fr Agent Frontend
 */

// Get configuration from global scope (only if not already defined)
if (typeof STORAGE_KEYS === 'undefined') {
    const STORAGE_KEYS = window.STORAGE_KEYS || {
        CONVERSATIONS: 'conversations',
        CURRENT_CONVERSATION: 'current_conversation',
        USER_PREFERENCES: 'user_preferences',
        THEME: 'theme',
        LANGUAGE: 'language'
    };
    window.STORAGE_KEYS = STORAGE_KEYS;
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
if (typeof StorageService === 'undefined') {
    class StorageService {
        constructor() {
            this.keys = window.STORAGE_KEYS;
        }

        /**
         * Set a value in localStorage
         */
        set(key, value) {
            try {
                const serializedValue = JSON.stringify(value);
                localStorage.setItem(key, serializedValue);
                window.Logger.debug(`💾 Stored: ${key} = ${typeof value === 'object' ? '[Object]' : value}`);
                return true;
            } catch (error) {
                window.Logger.error(`❌ Failed to store ${key}: ${error.message}`);
                return false;
            }
        }

        /**
         * Get a value from localStorage
         */
        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                if (item === null) {
                    return defaultValue;
                }
                
                const value = JSON.parse(item);
                window.Logger.debug(`📖 Retrieved: ${key} = ${typeof value === 'object' ? '[Object]' : value}`);
                return value;
            } catch (error) {
                window.Logger.error(`❌ Failed to retrieve ${key}: ${error.message}`);
                return defaultValue;
            }
        }

        /**
         * Remove a value from localStorage
         */
        remove(key) {
            try {
                localStorage.removeItem(key);
                window.Logger.debug(`🗑️ Removed: ${key}`);
                return true;
            } catch (error) {
                window.Logger.error(`❌ Failed to remove ${key}: ${error.message}`);
                return false;
            }
        }

        /**
         * Clear all localStorage
         */
        clear() {
            try {
                localStorage.clear();
                window.Logger.info(`🧹 Cleared all localStorage`);
                return true;
            } catch (error) {
                window.Logger.error(`❌ Failed to clear localStorage: ${error.message}`);
                return false;
            }
        }

        /**
         * Check if a key exists
         */
        has(key) {
            return localStorage.getItem(key) !== null;
        }

        /**
         * Get all keys
         */
        getAllKeys() {
            return Object.keys(localStorage);
        }

        /**
         * Get storage size in bytes
         */
        getSize() {
            let size = 0;
            for (let key in localStorage) {
                if (localStorage.hasOwnProperty(key)) {
                    size += localStorage[key].length + key.length;
                }
            }
            return size;
        }

        // Conversation-specific methods
        getConversationId() {
            return this.get(this.keys.CONVERSATION_ID);
        }

        setConversationId(conversationId) {
            return this.set(this.keys.CONVERSATION_ID, conversationId);
        }

        clearConversationId() {
            return this.remove(this.keys.CONVERSATION_ID);
        }

        // User preferences methods
        getUserPreferences() {
            return this.get(this.keys.USER_PREFERENCES, {});
        }

        setUserPreferences(preferences) {
            return this.set(this.keys.USER_PREFERENCES, preferences);
        }

        updateUserPreference(key, value) {
            const preferences = this.getUserPreferences();
            preferences[key] = value;
            return this.setUserPreferences(preferences);
        }

        getUserPreference(key, defaultValue = null) {
            const preferences = this.getUserPreferences();
            return preferences[key] !== undefined ? preferences[key] : defaultValue;
        }

        clearUserPreferences() {
            return this.remove(this.keys.USER_PREFERENCES);
        }

        // Chat history methods
        getChatHistory() {
            return this.get(this.keys.CHAT_HISTORY, []);
        }

        setChatHistory(history) {
            return this.set(this.keys.CHAT_HISTORY, history);
        }

        addChatMessage(message) {
            const history = this.getChatHistory();
            history.push({
                ...message,
                timestamp: new Date().toISOString()
            });
            
            // Keep only last 100 messages
            if (history.length > 100) {
                history.splice(0, history.length - 100);
            }
            
            return this.setChatHistory(history);
        }

        clearChatHistory() {
            return this.remove(this.keys.CHAT_HISTORY);
        }

        // Theme methods
        getTheme() {
            return this.get(this.keys.THEME, 'light');
        }

        setTheme(theme) {
            return this.set(this.keys.THEME, theme);
        }

        // Utility methods
        exportData() {
            const data = {};
            for (const key of Object.values(this.keys)) {
                data[key] = this.get(key);
            }
            return data;
        }

        importData(data) {
            try {
                for (const [key, value] of Object.entries(data)) {
                    if (Object.values(this.keys).includes(key)) {
                        this.set(key, value);
                    }
                }
                window.Logger.info(`✅ Data imported successfully`);
                return true;
            } catch (error) {
                window.Logger.error(`❌ Failed to import data: ${error.message}`);
                return false;
            }
        }

        /**
         * Migrate old storage keys to new ones
         */
        migrateStorage() {
            const migrations = [
                { old: 'layla_conversation_id', new: this.keys.CONVERSATION_ID },
                { old: 'layla_user_preferences', new: this.keys.USER_PREFERENCES },
                { old: 'layla_chat_history', new: this.keys.CHAT_HISTORY },
                { old: 'layla_theme', new: this.keys.THEME }
            ];

            for (const migration of migrations) {
                if (this.has(migration.old)) {
                    const value = this.get(migration.old);
                    this.set(migration.new, value);
                    this.remove(migration.old);
                    window.Logger.info(`🔄 Migrated: ${migration.old} → ${migration.new}`);
                }
            }
        }

        /**
         * Clean up expired data
         */
        cleanup() {
            const now = new Date();
            const maxAge = 30 * 24 * 60 * 60 * 1000; // 30 days

            // Clean up old chat history
            const history = this.getChatHistory();
            const filteredHistory = history.filter(message => {
                const messageDate = new Date(message.timestamp);
                return (now - messageDate) < maxAge;
            });

            if (filteredHistory.length !== history.length) {
                this.setChatHistory(filteredHistory);
                window.Logger.info(`🧹 Cleaned up ${history.length - filteredHistory.length} old messages`);
            }
        }
    }

    // Create and export singleton instance
    const storageService = new StorageService();

    // Make available globally
    window.storageService = storageService;
    window.StorageService = StorageService;
} 