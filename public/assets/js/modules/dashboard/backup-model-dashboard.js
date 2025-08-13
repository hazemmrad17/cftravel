/**
 * Backup Model Dashboard Module
 * Visual dashboard for managing priority-based backup models
 */

// Only create the class if it doesn't exist
if (typeof BackupModelDashboard === 'undefined') {
    class BackupModelDashboard {
    constructor() {
        this.apiBaseUrl = window.UnifiedConfig ? window.UnifiedConfig.getApiBaseUrl() : 'http://localhost:8000';
        this.dashboardContainer = null;
        this.isVisible = false;
    }

    /**
     * Initialize the dashboard
     */
    init() {
        this.createDashboard();
        this.loadModelStatus();
        this.attachEventListeners();
    }

    /**
     * Create the dashboard HTML structure
     */
    createDashboard() {
        const dashboardHTML = this.renderDashboardTemplate();
        
        const dashboard = document.createElement('div');
        dashboard.innerHTML = dashboardHTML;
        this.dashboardContainer = dashboard.firstElementChild;
        
        document.body.appendChild(this.dashboardContainer);
    }

    /**
     * Render dashboard template
     */
    renderDashboardTemplate() {
        return `
            <div id="backup-model-dashboard" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden">
                <div class="flex items-center justify-center min-h-screen p-4">
                    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
                        <!-- Header -->
                        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                            <div class="flex items-center space-x-3">
                                <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                                    </svg>
                                </div>
                                <div>
                                    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Backup Model Dashboard</h2>
                                    <p class="text-sm text-gray-600 dark:text-gray-400">Gestion des modèles de sauvegarde</p>
                                </div>
                            </div>
                            <button id="close-dashboard" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>

                        <!-- Content -->
                        <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
                            <!-- Status Overview -->
                            <div class="mb-8">
                                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Vue d'ensemble</h3>
                                <div id="status-overview" class="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <!-- Status cards will be populated by JavaScript -->
                                </div>
                            </div>

                            <!-- Model Types -->
                            <div class="space-y-6">
                                <div id="model-types">
                                    <!-- Model type sections will be populated by JavaScript -->
                                </div>
                            </div>

                            <!-- Action Buttons -->
                            <div class="flex justify-center space-x-4 mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                                <button id="test-all-models" 
                                        class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                                    <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                    Tester tous les modèles
                                </button>
                                <button id="close-dashboard-btn" 
                                        class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                                    Fermer
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Load model status from API
     */
    async loadModelStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/models/backup/status`);
            if (response.ok) {
                const data = await response.json();
                this.updateStatusOverview(data);
                this.updateModelTypes(data);
            } else {
                console.error('Failed to load model status');
                this.showError('Failed to load model status');
            }
        } catch (error) {
            console.error('Error loading model status:', error);
            this.showError('Error loading model status');
        }
    }

    /**
     * Update status overview section
     */
    updateStatusOverview(data) {
        const statusOverview = document.getElementById('status-overview');
        if (!statusOverview) return;

        const statusCards = [
            {
                title: 'Modèles Actifs',
                value: data.active_models || 0,
                status: 'success',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
            },
            {
                title: 'Modèles de Sauvegarde',
                value: data.backup_models || 0,
                status: 'warning',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>'
            },
            {
                title: 'Modèles Testés',
                value: data.tested_models || 0,
                status: 'success',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
            },
            {
                title: 'Modèles Échoués',
                value: data.failed_models || 0,
                status: 'error',
                icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>'
            }
        ];

        statusOverview.innerHTML = statusCards.map(card => this.renderStatusCard(card)).join('');
    }

    /**
     * Render status card
     */
    renderStatusCard(card) {
        const statusColors = {
            success: 'green',
            warning: 'yellow',
            error: 'red'
        };
        
        const color = statusColors[card.status];
        
        return `
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 ${color === 'green' ? 'bg-green-100 dark:bg-green-900' : color === 'yellow' ? 'bg-yellow-100 dark:bg-yellow-900' : 'bg-red-100 dark:bg-red-900'} rounded-lg flex items-center justify-center">
                            <svg class="w-5 h-5 ${color === 'green' ? 'text-green-600 dark:text-green-400' : color === 'yellow' ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                ${card.icon}
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">${card.title}</p>
                            <p class="text-lg font-bold text-gray-900 dark:text-white">${card.value}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Update model types section
     */
    updateModelTypes(data) {
        const modelTypes = document.getElementById('model-types');
        if (!modelTypes) return;

        const modelTypeData = {
            reasoning: data.reasoning || {},
            generation: data.generation || {},
            matcher: data.matcher || {},
            extractor: data.extractor || {}
        };

        modelTypes.innerHTML = Object.entries(modelTypeData).map(([type, typeData]) => 
            this.renderModelTypeSection(type, typeData)
        ).join('');
    }

    /**
     * Render model type section
     */
    renderModelTypeSection(type, data) {
        const typeNames = {
            reasoning: 'Raisonnement',
            generation: 'Génération',
            matcher: 'Correspondance',
            extractor: 'Extraction'
        };

        const typeColors = {
            reasoning: 'blue',
            generation: 'purple',
            matcher: 'orange',
            extractor: 'green'
        };

        const color = typeColors[type];
        const name = typeNames[type];

        return `
            <div class="bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden">
                <div class="bg-gray-50 dark:bg-gray-600 px-6 py-4 border-b border-gray-200 dark:border-gray-500">
                    <h4 class="text-lg font-semibold text-gray-900 dark:text-white capitalize">${name}</h4>
                </div>
                <div class="p-6">
                    <!-- Primary Model -->
                    <div class="mb-6">
                        <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Modèle Principal</h5>
                        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
                            <div class="flex items-center justify-between">
                                <div>
                                    <p class="font-medium text-blue-900 dark:text-blue-100">${data.primary?.name || 'Non configuré'}</p>
                                    <p class="text-sm text-blue-700 dark:text-blue-300">
                                        Temp: ${data.primary?.temperature || 'N/A'} | Tokens: ${data.primary?.max_tokens || 'N/A'}
                                    </p>
                                </div>
                                <span class="px-2 py-1 bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 text-xs rounded-full">
                                    Principal
                                </span>
                            </div>
                        </div>
                    </div>

                    <!-- Backup Models -->
                    <div>
                        <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Modèles de Sauvegarde</h5>
                        <div class="space-y-3">
                            ${(data.backups || []).map(backup => `
                                <div class="bg-gray-50 dark:bg-gray-600 rounded-lg p-4 border border-gray-200 dark:border-gray-500">
                                    <div class="flex items-center justify-between">
                                        <div>
                                            <p class="font-medium text-gray-900 dark:text-white">${backup.name}</p>
                                            <p class="text-sm text-gray-600 dark:text-gray-400">
                                                Temp: ${backup.temperature} | Tokens: ${backup.max_tokens} | Priorité: ${backup.priority}
                                            </p>
                                        </div>
                                        <span class="px-2 py-1 bg-gray-100 dark:bg-gray-500 text-gray-700 dark:text-gray-300 text-xs rounded-full">
                                            Sauvegarde ${backup.priority}
                                        </span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Close button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'close-dashboard' || e.target.id === 'close-dashboard-btn') {
                this.hide();
            }
        });

        // Test all models button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'test-all-models') {
                this.testAllModels();
            }
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (e.target.id === 'backup-model-dashboard') {
                this.hide();
            }
        });
    }

    /**
     * Show the dashboard
     */
    show() {
        if (this.dashboardContainer) {
            this.dashboardContainer.classList.remove('hidden');
            this.isVisible = true;
            this.loadModelStatus(); // Refresh data when showing
        }
    }

    /**
     * Hide the dashboard
     */
    hide() {
        if (this.dashboardContainer) {
            this.dashboardContainer.classList.add('hidden');
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
     * Test all models
     */
    async testAllModels() {
        try {
            const button = document.getElementById('test-all-models');
            const originalText = button.innerHTML;
            
            // Show loading state
            button.innerHTML = `
                <svg class="animate-spin w-5 h-5 inline mr-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Test en cours...
            `;
            button.disabled = true;

            const response = await fetch(`${this.apiBaseUrl}/models/backup/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccess('Tous les modèles ont été testés avec succès');
                this.loadModelStatus(); // Refresh data
            } else {
                this.showError('Erreur lors du test des modèles');
            }
        } catch (error) {
            console.error('Error testing models:', error);
            this.showError('Erreur lors du test des modèles');
        } finally {
            // Restore button state
            const button = document.getElementById('test-all-models');
            button.innerHTML = `
                <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Tester tous les modèles
            `;
            button.disabled = false;
        }
    }

    /**
     * Test specific model type
     */
    async testModelType(modelType) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/models/backup/test/${modelType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccess(`Modèle ${modelType} testé avec succès`);
                this.loadModelStatus(); // Refresh data
            } else {
                this.showError(`Erreur lors du test du modèle ${modelType}`);
            }
        } catch (error) {
            console.error(`Error testing model ${modelType}:`, error);
            this.showError(`Erreur lors du test du modèle ${modelType}`);
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
    const backupModelDashboard = new BackupModelDashboard();

    // Make available globally
    window.BackupModelDashboard = backupModelDashboard;
    window.backupModelDashboard = backupModelDashboard;
} 