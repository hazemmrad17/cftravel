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
                '/assets/js/modules/chat/offer-display.js',
                
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

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🌐 Application starting...');
    
    try {
        await ModuleLoader.loadModules();
        
        // Initialize global application state
        window.App = {
            modules: {
                chat: window.chatCore,
                offers: window.OfferDisplay,
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
        
        if (window.chatCore) {
            try {
                console.log('🚀 Initializing chat core...');
                // Add a small delay to ensure DOM elements are ready
                await new Promise(resolve => setTimeout(resolve, 100));
                await window.chatCore.init();
                console.log('✅ Chat core initialized successfully');
            } catch (error) {
                console.error('❌ Failed to initialize chat core:', error);
            }
        } else {
            console.warn('⚠️ Chat core not available for initialization');
        }
        
    } catch (error) {
        console.error('❌ Application initialization failed:', error);
    }
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('🚨 Global error:', event.error);
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('🚨 Unhandled promise rejection:', event.reason);
});
