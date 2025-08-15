/**
 * Main Application Entry Point
 * Loads and initializes all modules in the correct order
 */

// Module loader utility
if (typeof ModuleLoader === 'undefined') {
    class ModuleLoader {
        static async loadScript(src) {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = src;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }

        static async loadModules() {
            const modules = [
                // Core utilities and configuration
                '/assets/js/config/unified-config.js',
                '/assets/js/core/utils.js',
                
                // Services
                '/assets/js/services/api.service.js',
                '/assets/js/services/chat.service.js',
                '/assets/js/services/storage.service.js',
                
                // Chat modules
                '/assets/js/modules/chat/chat-core.js',
                
                // Confirmation modules
                '/assets/js/modules/confirmation/confirmation-flow.js',
                
                // Dashboard modules
                '/assets/js/modules/dashboard/backup-model-dashboard.js',
                '/assets/js/modules/dashboard/model-manager.js'
            ];

            console.log('🚀 Loading application modules...');
            
            for (const module of modules) {
                try {
                    await this.loadScript(module);
                    console.log(`✅ Loaded: ${module}`);
                } catch (error) {
                    console.error(`❌ Failed to load: ${module}`, error);
                }
            }
            
            console.log('🎉 All modules loaded successfully');
        }
    }

    // Make ModuleLoader available globally
    window.ModuleLoader = ModuleLoader;
}

// Global error handler for layout issues
window.addEventListener('error', function(event) {
    if (event.message && event.message.includes('Layout was forced before the page was fully loaded')) {
        console.warn('⚠️ Layout issue detected - this is a common browser warning that can be safely ignored');
        event.preventDefault();
        return false;
    }
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    if (event.reason && event.reason.message && event.reason.message.includes('Layout was forced before the page was fully loaded')) {
        console.warn('⚠️ Layout issue detected in promise - this is a common browser warning');
        event.preventDefault();
        return false;
    }
});

// Optimize page load performance
document.addEventListener('DOMContentLoaded', function() {
    // Ensure all stylesheets are loaded before any layout operations
    const stylesheets = Array.from(document.styleSheets);
    const pendingStylesheets = stylesheets.filter(sheet => {
        try {
            return sheet.href && !sheet.href.startsWith('data:');
        } catch (e) {
            return false;
        }
    });
    
    if (pendingStylesheets.length > 0) {
        console.log('📦 Waiting for stylesheets to load...');
        Promise.all(pendingStylesheets.map(sheet => {
            return new Promise((resolve) => {
                if (sheet.href) {
                    const link = document.querySelector(`link[href="${sheet.href}"]`);
                    if (link) {
                        link.addEventListener('load', resolve);
                        link.addEventListener('error', resolve); // Continue even if some fail
                    } else {
                        resolve();
                    }
                } else {
                    resolve();
                }
            });
        })).then(() => {
            console.log('✅ All stylesheets loaded');
            // Initialize app after stylesheets are loaded
            initializeApp();
        });
    } else {
        // No external stylesheets, initialize immediately
        initializeApp();
    }
});

async function initializeApp() {
    console.log('🌐 Application starting...');
    
    try {
        await ModuleLoader.loadModules();
        
        // Initialize global application state
        window.App = {
            modules: {
                chat: window.chatCore,
                confirmation: window.confirmationFlow,
                backupDashboard: window.BackupModelDashboard,
                modelManager: window.modelManager
            },
            
            // Global utility methods
            utils: {
                showNotification: (message, type = 'info') => {
                    // Implementation for notifications
                    console.log(`[${type.toUpperCase()}] ${message}`);
                },
                
                formatDate: (date) => {
                    return new Date(date).toLocaleDateString('fr-FR');
                },
                
                debounce: (func, wait) => {
                    let timeout;
                    return function executedFunction(...args) {
                        const later = () => {
                            clearTimeout(timeout);
                            func(...args);
                        };
                        clearTimeout(timeout);
                        timeout = setTimeout(later, wait);
                    };
                }
            }
        };
        
        console.log('✅ Application initialized successfully');
        
        // Initialize chat core if available
        console.log('🔍 Checking for chatCore availability...');
        console.log('window.chatCore:', window.chatCore);
        
        if (window.chatCore && !window.chatCore.initialized) {
            try {
                console.log('🚀 Initializing chat core...');
                await window.chatCore.init();
                console.log('✅ Chat core initialized successfully');
            } catch (error) {
                console.error('❌ Failed to initialize chat core:', error);
            }
        } else if (window.chatCore && window.chatCore.initialized) {
            console.log('✅ Chat core already initialized');
        } else {
            console.warn('⚠️ Chat core not available for initialization');
        }
        
    } catch (error) {
        console.error('❌ Application initialization failed:', error);
    }
}
