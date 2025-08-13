/**
 * Model Manager Module
 * Frontend interface for managing AI model switches and configurations
 */

// Only create the class if it doesn't exist
if (typeof ModelManager === 'undefined') {
    class ModelManager {
    constructor() {
        this.apiBaseUrl = window.UnifiedConfig ? window.UnifiedConfig.getApiBaseUrl() : 'http://localhost:8000';
        this.modelData = null;
        this.dashboardContainer = null;
        this.isVisible = false;
    }
    
    async init() {
        await this.loadModelConfiguration();
        this.createDashboard();
        this.attachEventListeners();
    }
    
    async loadModelConfiguration() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/models`);
            if (response.ok) {
                this.modelData = await response.json();
                console.log('🔧 Model configuration loaded:', this.modelData);
            } else {
                console.error('Failed to load model configuration');
                this.modelData = null;
            }
        } catch (error) {
            console.error('Error loading model configuration:', error);
            this.modelData = null;
        }
    }
    
    createDashboard() {
        const dashboardHTML = this.renderDashboardTemplate();
        
        const dashboard = document.createElement('div');
        dashboard.innerHTML = dashboardHTML;
        this.dashboardContainer = dashboard.firstElementChild;
        
        document.body.appendChild(this.dashboardContainer);
    }
    
    renderDashboardTemplate() {
        return `
            <div id="model-manager-dashboard" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" style="display: none;">
                <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold text-gray-800 dark:text-white">🤖 AI Model Manager</h2>
                        <button id="close-model-manager" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Model Switches -->
                        <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                            <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-white">🔌 Model Switches</h3>
                            <div id="model-switches" class="space-y-3">
                                <!-- Switches will be populated here -->
                            </div>
                        </div>
                        
                        <!-- Model Status -->
                        <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                            <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-white">📊 Model Status</h3>
                            <div id="model-status" class="space-y-2">
                                <!-- Status will be populated here -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Available Models -->
                    <div class="mt-6 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                        <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-white">📚 Available Models</h3>
                        <div id="available-models" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <!-- Available models will be populated here -->
                        </div>
                    </div>
                    
                    <!-- Validation -->
                    <div class="mt-6 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                        <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-white">✅ Configuration Validation</h3>
                        <div id="validation-status">
                            <!-- Validation will be populated here -->
                        </div>
                    </div>
                    
                    <div class="mt-6 flex justify-end space-x-3">
                        <button id="refresh-models" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
                            🔄 Refresh
                        </button>
                        <button id="save-model-config" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors">
                            💾 Save Configuration
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    attachEventListeners() {
        // Close button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'close-model-manager') {
                this.hide();
            }
        });

        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'refresh-models') {
                this.refreshModels();
            }
        });

        // Save configuration button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'save-model-config') {
                this.saveConfiguration();
            }
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (e.target.id === 'model-manager-dashboard') {
                this.hide();
            }
        });
    }

    /**
     * Show the dashboard
     */
    show() {
        if (this.dashboardContainer) {
            this.dashboardContainer.style.display = 'flex';
            this.isVisible = true;
            this.populateDashboard();
        }
    }

    /**
     * Hide the dashboard
     */
    hide() {
        if (this.dashboardContainer) {
            this.dashboardContainer.style.display = 'none';
            this.isVisible = false;
        }
    }

    /**
     * Toggle dashboard visibility
     */
    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    /**
     * Populate dashboard with data
     */
    populateDashboard() {
        this.populateModelSwitches();
        this.populateModelStatus();
        this.populateAvailableModels();
        this.populateValidationStatus();
    }

    /**
     * Populate model switches section
     */
    populateModelSwitches() {
        const switchesContainer = document.getElementById('model-switches');
        if (!switchesContainer || !this.modelData) return;

        const switches = this.modelData.switches || {};
        const switchesHTML = Object.entries(switches).map(([modelType, isEnabled]) => `
            <div class="flex items-center justify-between p-3 bg-white dark:bg-gray-600 rounded-lg border border-gray-200 dark:border-gray-500">
                <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                        <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                    <div>
                        <p class="font-medium text-gray-800 dark:text-white capitalize">${modelType}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">AI Model</p>
                    </div>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" class="sr-only peer" ${isEnabled ? 'checked' : ''} 
                           onchange="modelManager.toggleModelSwitch('${modelType}', this.checked)">
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
            </div>
        `).join('');

        switchesContainer.innerHTML = switchesHTML;
    }

    /**
     * Populate model status section
     */
    populateModelStatus() {
        const statusContainer = document.getElementById('model-status');
        if (!statusContainer || !this.modelData) return;

        const models = this.modelData.models || {};
        const statusHTML = Object.entries(models).map(([modelType, modelConfig]) => `
            <div class="flex items-center justify-between p-3 bg-white dark:bg-gray-600 rounded-lg border border-gray-200 dark:border-gray-500">
                <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 ${modelConfig.enabled ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'} rounded-lg flex items-center justify-center">
                        <svg class="w-4 h-4 ${modelConfig.enabled ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div>
                        <p class="font-medium text-gray-800 dark:text-white capitalize">${modelType}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">${modelConfig.name || 'Not configured'}</p>
                    </div>
                </div>
                <span class="px-2 py-1 text-xs rounded-full ${modelConfig.enabled ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}">
                    ${modelConfig.enabled ? 'Active' : 'Inactive'}
                </span>
            </div>
        `).join('');

        statusContainer.innerHTML = statusHTML;
    }

    /**
     * Populate available models section
     */
    populateAvailableModels() {
        const modelsContainer = document.getElementById('available-models');
        if (!modelsContainer || !this.modelData) return;

        const availableModels = this.modelData.available_models || [];
        const modelsHTML = availableModels.map(model => `
            <div class="bg-white dark:bg-gray-600 rounded-lg p-4 border border-gray-200 dark:border-gray-500">
                <div class="flex items-center justify-between mb-2">
                    <h4 class="font-medium text-gray-800 dark:text-white">${model.name}</h4>
                    <span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        ${model.provider}
                    </span>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">${model.description || 'No description available'}</p>
                <div class="flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
                    <span>Temp: ${model.temperature || 'N/A'}</span>
                    <span>Tokens: ${model.max_tokens || 'N/A'}</span>
                </div>
            </div>
        `).join('');

        modelsContainer.innerHTML = modelsHTML;
    }

    /**
     * Populate validation status section
     */
    populateValidationStatus() {
        const validationContainer = document.getElementById('validation-status');
        if (!validationContainer || !this.modelData) return;

        const validation = this.modelData.validation || {};
        const validationHTML = `
            <div class="space-y-3">
                <div class="flex items-center justify-between p-3 bg-white dark:bg-gray-600 rounded-lg border border-gray-200 dark:border-gray-500">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 ${validation.config_valid ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'} rounded-lg flex items-center justify-center">
                            <svg class="w-4 h-4 ${validation.config_valid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="font-medium text-gray-800 dark:text-white">Configuration</p>
                            <p class="text-sm text-gray-500 dark:text-gray-400">Model settings validation</p>
                        </div>
                    </div>
                    <span class="px-2 py-1 text-xs rounded-full ${validation.config_valid ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}">
                        ${validation.config_valid ? 'Valid' : 'Invalid'}
                    </span>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-white dark:bg-gray-600 rounded-lg border border-gray-200 dark:border-gray-500">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 ${validation.api_accessible ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'} rounded-lg flex items-center justify-center">
                            <svg class="w-4 h-4 ${validation.api_accessible ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="font-medium text-gray-800 dark:text-white">API Access</p>
                            <p class="text-sm text-gray-500 dark:text-gray-400">External API connectivity</p>
                        </div>
                    </div>
                    <span class="px-2 py-1 text-xs rounded-full ${validation.api_accessible ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}">
                        ${validation.api_accessible ? 'Connected' : 'Disconnected'}
                    </span>
                </div>
            </div>
        `;

        validationContainer.innerHTML = validationHTML;
    }

    /**
     * Toggle model switch
     */
    async toggleModelSwitch(modelType, enabled) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/models/switch/${modelType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    enabled: enabled
                })
            });

            if (response.ok) {
                this.showSuccess(`${modelType} model ${enabled ? 'enabled' : 'disabled'} successfully`);
                await this.loadModelConfiguration(); // Refresh data
                this.populateDashboard(); // Update UI
            } else {
                this.showError(`Failed to ${enabled ? 'enable' : 'disable'} ${modelType} model`);
            }
        } catch (error) {
            console.error(`Error toggling ${modelType} model:`, error);
            this.showError(`Error toggling ${modelType} model`);
        }
    }

    /**
     * Refresh models
     */
    async refreshModels() {
        try {
            await this.loadModelConfiguration();
            this.populateDashboard();
            this.showSuccess('Model configuration refreshed successfully');
        } catch (error) {
            console.error('Error refreshing models:', error);
            this.showError('Error refreshing models');
        }
    }

    /**
     * Save configuration
     */
    async saveConfiguration() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/models/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.modelData)
            });

            if (response.ok) {
                this.showSuccess('Configuration saved successfully');
            } else {
                this.showError('Failed to save configuration');
            }
        } catch (error) {
            console.error('Error saving configuration:', error);
            this.showError('Error saving configuration');
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-green-500 text-white' : 
            type === 'error' ? 'bg-red-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    }

    // Create and export singleton instance
    const modelManager = new ModelManager();

    // Make available globally
    window.ModelManager = modelManager;
    window.modelManager = modelManager;
} 