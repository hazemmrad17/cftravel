/**
 * Core configuration for ASIA.fr Agent Frontend
 */

// API Configuration
export const API_CONFIG = {
    BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:8002' 
        : 'https://ovg-iagent.cftravel.net:8000',
    ENDPOINTS: {
        CHAT: '/chat',
        CHAT_STREAM: '/chat/stream',
        OFFERS: '/offers',
        PREFERENCES: '/preferences',
        MEMORY_CLEAR: '/chat/memory/clear',
        WELCOME: '/welcome',
        STATUS: '/status'
    },
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3
};

// UI Configuration
export const UI_CONFIG = {
    ANIMATION_DURATION: 300,
    TYPING_SPEED: 50,
    MAX_MESSAGE_LENGTH: 1000,
    AUTO_SCROLL_DELAY: 100,
    LOADING_TIMEOUT: 10000
};

// Chat Configuration
export const CHAT_CONFIG = {
    MAX_MESSAGES: 100,
    MESSAGE_TYPES: {
        USER: 'user',
        ASSISTANT: 'assistant',
        SYSTEM: 'system',
        ERROR: 'error'
    },
    STREAMING: {
        CHUNK_DELAY: 50,
        END_MARKER: 'data: {"type": "end"}'
    }
};

// Offer Configuration
export const OFFER_CONFIG = {
    MAX_OFFERS: 3,
    CARD_ANIMATION_DELAY: 200,
    IMAGE_PLACEHOLDER: '/assets/images/placeholder-travel.svg',
    RATING_DEFAULT: 4.5,
    PRICE_RANGES: {
        BUDGET: '€€',
        MID_RANGE: '€€€',
        LUXURY: '€€€€'
    }
};

// Storage Keys
export const STORAGE_KEYS = {
    CONVERSATION_ID: 'asia_conversation_id',
    USER_PREFERENCES: 'asia_user_preferences',
    CHAT_HISTORY: 'asia_chat_history',
    THEME: 'asia_theme'
};

// Event Names
export const EVENTS = {
    MESSAGE_SENT: 'message:sent',
    MESSAGE_RECEIVED: 'message:received',
    OFFERS_DISPLAYED: 'offers:displayed',
    OFFER_SELECTED: 'offer:selected',
    ERROR_OCCURRED: 'error:occurred',
    STATE_CHANGED: 'state:changed'
};

// Debug Configuration
export const DEBUG_CONFIG = {
    ENABLED: true,
    LOG_LEVEL: 'info', // 'debug', 'info', 'warn', 'error'
    LOG_PREFIX: '[ASIA]'
}; 