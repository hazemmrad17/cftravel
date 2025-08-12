/**
 * Environment Configuration
 * Manages API URLs and other settings for different environments
 */

const Config = {
    // API Configuration
    getApiBaseUrl: function() {
        const hostname = window.location.hostname;
        
        // Production environments
        if (hostname === 'ovg-iagent.cftravel.net' || 
            hostname === 'iagent.cftravel.net' ||
            hostname.includes('cftravel.net')) {
            return 'https://ovg-iagent.cftravel.net';
        }
        
        // Local development
        if (hostname === 'localhost' || 
            hostname === '127.0.0.1' ||
            hostname.includes('local')) {
            return 'http://localhost:8000';
        }
        
        // Default fallback
        return 'http://localhost:8000';
    },
    
    // Debug mode
    isDebug: function() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1';
    },
    
    // Log configuration for debugging
    logConfig: function() {
        if (this.isDebug()) {
            console.log('🔧 Environment Configuration:');
            console.log('  Hostname:', window.location.hostname);
            console.log('  API URL:', this.getApiBaseUrl());
            console.log('  Debug Mode:', this.isDebug());
        }
    }
};

// Auto-log configuration on load
Config.logConfig(); 