/**
 * Environment Configuration
 * Manages API URLs and other settings for different environments
 */

const Config = {
    // API Configuration
    getApiBaseUrl: function() {
        const hostname = window.location.hostname;
        
        // Force local development for testing (comment out when deploying)
        if (window.location.search.includes('local=true')) {
            const protocol = window.location.protocol;
            return `${protocol}//localhost:8002`;
        }
        
        // Production environments
        if (hostname === 'ovg-iagent.cftravel.net' || 
            hostname === 'iagent.cftravel.net' ||
            hostname.includes('cftravel.net')) {
            return 'https://ovg-iagent.cftravel.net/api-proxy.php';
        }
        
        // Local development
        if (hostname === 'localhost' || 
            hostname === '127.0.0.1' ||
            hostname.includes('local')) {
            // Use HTTPS if the page is served over HTTPS, otherwise HTTP
            const protocol = window.location.protocol;
            return `${protocol}//localhost:8002`;
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