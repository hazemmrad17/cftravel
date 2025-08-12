/**
 * Environment Configuration
 * Manages API URLs and other settings for different environments
 */

const Config = {
    // API Configuration
    getApiBaseUrl: function() {
        const hostname = window.location.hostname;
        
        // Force local development for testing (add ?local=true to URL)
        if (window.location.search.includes('local=true')) {
            return 'http://localhost:8002';
        }
        
        // Local development
        if (hostname === 'localhost' || 
            hostname === '127.0.0.1' ||
            hostname.includes('local')) {
            return 'http://localhost:8002';
        }
        
        // Production - use production API
        if (hostname === 'ovg-iagent.cftravel.net' || 
            hostname === 'iagent.cftravel.net' ||
            hostname.includes('cftravel.net')) {
            return 'https://ovg-iagent.cftravel.net:8000'; // Production API on port 8000
        }
        
        // Default fallback
        return 'http://localhost:8002';
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