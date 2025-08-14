/**
 * Confirmation Flow Handler for ASIA.fr Agent
 * Handles the confirmation flow when users provide sufficient travel details
 */

    class ConfirmationFlow {
        constructor() {
        this.API_BASE_URL = window.UnifiedConfig ? window.UnifiedConfig.getApiBaseUrl() : '/api';
            this.currentState = null;
            this.preferences = {};
            this.offersData = new Map(); // Store offers data separately to avoid HTML attribute size limits
        
            
            this.init();
            
            // Initialize Lucide icons with a small delay to ensure DOM is ready
            setTimeout(() => {
                this.initializeLucideIcons();
            }, 100);
        }
        
        /**
         * Initialize Lucide icons
         */
        initializeLucideIcons() {
            console.log('Initializing Lucide icons...');
            if (typeof lucide !== 'undefined') {
                console.log('Lucide library found, creating icons...');
                lucide.createIcons();
                console.log('Lucide icons initialized successfully');
            } else {
                console.error('Lucide library not found! Retrying in 500ms...');
                // Retry after a delay in case the script loads after our initialization
                setTimeout(() => {
                    this.initializeLucideIcons();
                }, 500);
            }
        }
        
        /**
         * Refresh Lucide icons for dynamically added content
         */
        refreshLucideIcons() {
            console.log('Refreshing Lucide icons...');
            if (typeof lucide !== 'undefined') {
                console.log('Lucide library found, refreshing icons...');
                lucide.createIcons();
                console.log('Lucide icons refreshed successfully');
            } else {
                console.error('Lucide library not found during refresh! Retrying in 500ms...');
                // Retry after a delay in case the script loads after our refresh
                setTimeout(() => {
                    this.refreshLucideIcons();
                }, 500);
            }
        }


        // Helper methods for color management
        getCurrentMode() {
            const isDarkMode = document.documentElement.classList.contains('dark');
        return isDarkMode ? 'dark' : 'light';
        }

    // Initialize test functionality
        /**
         * Display confirmation request with user preferences
         */
        displayConfirmationRequest(preferences, confirmationSummary) {
        const chatArea = document.querySelector('.chat-messages');
            if (!chatArea) return;
            
            const confirmationDiv = document.createElement('div');
            confirmationDiv.className = 'flex justify-start mb-6 animate-fade-in';
        confirmationDiv.innerHTML = `
                <div class="bg-white dark:bg-gray-800 shadow-2xl rounded-3xl rounded-bl-lg p-8 max-w-6xl border border-gray-100 dark:border-gray-700 backdrop-blur-sm relative overflow-hidden">
                    <!-- Background decorative elements -->
                    <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-emerald-100 to-teal-200 dark:from-emerald-900/20 dark:to-teal-800/20 rounded-full -translate-y-16 translate-x-16 opacity-60"></div>
                    <div class="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-blue-100 to-indigo-200 dark:from-blue-900/20 dark:to-indigo-800/20 rounded-full translate-y-12 -translate-x-12 opacity-60"></div>
                    
                    <!-- Enhanced Header with better visual hierarchy -->
                    <div class="text-center mb-8 relative z-10">
                        <h2 class="text-3xl font-bold bg-gradient-to-r from-gray-800 to-black bg-clip-text text-transparent mb-3">Parfait !</h2>
                        <p class="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
                            J'ai rassemblé tous les détails nécessaires pour trouver vos offres de voyage parfaites
                        </p>
                    </div>

                    <!-- Enhanced Preferences Summary with better cards -->
                    <div class="mb-8">
                        <div class="text-center mb-6">
                            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
                                Vos Préférences de Voyage
                            </h3>
                            <div class="w-16 h-1 bg-gradient-to-r from-gray-800 to-black mx-auto rounded-full"></div>
                        </div>
                        <div class="bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-700 dark:via-gray-800 dark:to-gray-700 rounded-3xl p-6 border border-gray-200 dark:border-gray-600 shadow-xl backdrop-blur-sm">
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                ${this.renderEnhancedPreferenceItems(preferences)}
                            </div>
                        </div>
                    </div>

                    <!-- Enhanced confirmation message with better styling -->
                    <div class="mb-8">
                        <div class="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 rounded-3xl p-6 border border-blue-200 dark:border-blue-700 shadow-xl backdrop-blur-sm relative overflow-hidden">
                            <div class="flex items-start relative z-10">
                                <i data-lucide="sparkles" class="w-6 h-6 mr-4"></i>
                                <div class="flex-1">
                                    <h4 class="font-bold text-lg mb-3 text-gray-900 dark:text-white">Prêt à découvrir vos offres parfaites !</h4>
                                    <p class="text-base leading-relaxed text-gray-700 dark:text-gray-300">
                                        Basé sur vos préférences, je vais vous montrer les <strong class="text-blue-600 dark:text-blue-400">3 meilleures offres de voyage</strong> qui correspondent exactement à ce que vous recherchez. 
                                        Chaque offre sera soigneusement sélectionnée et classée par notre IA pour garantir la correspondance parfaite.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Enhanced Action Buttons with better styling -->
                    <div class="flex flex-col sm:flex-row gap-6 justify-center">
                        <button onclick="confirmationFlow.confirmPreferences()" 
                                class="group bg-gradient-to-r from-red-500 via-red-600 to-red-700 hover:from-red-600 hover:via-red-700 hover:to-red-800 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-2xl shadow-xl flex items-center justify-center relative overflow-hidden">
                            <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                            <i data-lucide="eye" class="w-6 h-6 mr-3 relative z-10 group-hover:animate-bounce"></i>
                            <span class="relative z-10">Oui, montrez-moi les offres !</span>
                        </button>
                        <button onclick="confirmationFlow.modifyPreferences()" 
                                class="group bg-gradient-to-r from-gray-900 via-black to-gray-900 hover:from-black hover:via-gray-900 hover:to-black text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-2xl shadow-xl flex items-center justify-center relative overflow-hidden border border-gray-700/30">
                            <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                            <i data-lucide="edit-3" class="w-6 h-6 mr-3 relative z-10 group-hover:animate-pulse"></i>
                            <span class="relative z-10">Je veux modifier quelque chose</span>
                        </button>
                    </div>
                </div>
            `;

        chatArea.appendChild(confirmationDiv);
        chatArea.scrollTop = chatArea.scrollHeight;

        // Store current preferences
        this.preferences = preferences;
        
        // Refresh Lucide icons for the new content
        this.refreshLucideIcons();
    }

    /**
     * Render preference items in a grid
     */
    renderPreferenceItems(preferences) {
        const items = [];
        
        if (preferences.destination) {
            items.push(`
                <div class="preference-item">
                    <div class="flex items-center">
                        <div class="preference-icon bg-gradient-to-r from-blue-500 to-indigo-600">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-bold text-mode-primary mb-1">Destination</p>
                            <p class="text-sm text-mode-secondary font-medium">${preferences.destination}</p>
                        </div>
                    </div>
                </div>
            `);
        }

        if (preferences.duration) {
            items.push(`
                <div class="preference-item">
                    <div class="flex items-center">
                        <div class="preference-icon bg-gradient-to-r from-emerald-500 to-teal-600">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-bold text-mode-primary mb-1">Durée</p>
                            <p class="text-sm text-mode-secondary font-medium">${preferences.duration} jours</p>
                        </div>
                    </div>
                </div>
            `);
        }

        if (preferences.style) {
            items.push(`
                <div class="preference-item">
                    <div class="flex items-center">
                        <div class="preference-icon bg-gradient-to-r from-purple-500 to-pink-600">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-bold text-mode-primary mb-1">Style de voyage</p>
                            <p class="text-sm text-mode-secondary font-medium">${preferences.style}</p>
                        </div>
                    </div>
                </div>
            `);
        }

        if (preferences.budget) {
            items.push(`
                <div class="preference-item">
                    <div class="flex items-center">
                        <div class="preference-icon bg-gradient-to-r from-amber-500 to-orange-600">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-bold text-mode-primary mb-1">Budget</p>
                            <p class="text-sm text-mode-secondary font-medium">${preferences.budget}</p>
                        </div>
                    </div>
                </div>
            `);
        }

        if (preferences.travelers) {
            items.push(`
                <div class="preference-item">
                    <div class="flex items-center">
                        <div class="preference-icon bg-gradient-to-r from-indigo-500 to-purple-600">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-bold text-mode-primary mb-1">Voyageurs</p>
                            <p class="text-sm text-mode-secondary font-medium">${preferences.travelers} personnes</p>
                        </div>
                    </div>
                </div>
            `);
        }

        if (preferences.timing) {
            items.push(`
                <div class="preference-item">
                    <div class="flex items-center">
                        <div class="preference-icon bg-gradient-to-r from-teal-500 to-cyan-600">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-bold text-mode-primary mb-1">Timing</p>
                            <p class="text-sm text-mode-secondary font-medium">${preferences.timing}</p>
                        </div>
                    </div>
                </div>
            `);
        }

        return items.join('');
        }

        /**
         * Render enhanced preference items with better styling
         */
        renderEnhancedPreferenceItems(preferences) {
            const items = [];
            
            if (preferences.destination) {
                items.push(`
                    <div class="preference-item group hover:scale-105 transition-all duration-300">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-lg border border-gray-200 dark:border-gray-600 hover:shadow-xl transition-all duration-300 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-200 dark:from-blue-900/20 dark:to-indigo-800/20 rounded-full -translate-y-8 translate-x-8 opacity-60"></div>
                            <div class="flex items-center relative z-10">
                                <i data-lucide="map-pin" class="w-6 h-6 mr-4"></i>
                                <div class="flex-1">
                                    <p class="text-sm font-bold text-gray-900 dark:text-white mb-1">Destination</p>
                                    <p class="text-base text-gray-700 dark:text-gray-300 font-semibold">${preferences.destination}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            }

            if (preferences.duration) {
                items.push(`
                    <div class="preference-item group hover:scale-105 transition-all duration-300">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-lg border border-gray-200 dark:border-gray-600 hover:shadow-xl transition-all duration-300 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-emerald-100 to-teal-200 dark:from-emerald-900/20 dark:to-teal-800/20 rounded-full -translate-y-8 translate-x-8 opacity-60"></div>
                            <div class="flex items-center relative z-10">
                                <i data-lucide="clock" class="w-6 h-6 mr-4"></i>
                                <div class="flex-1">
                                    <p class="text-sm font-bold text-gray-900 dark:text-white mb-1">Durée</p>
                                    <p class="text-base text-gray-700 dark:text-gray-300 font-semibold">${preferences.duration} jours</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            }

            if (preferences.style) {
                items.push(`
                    <div class="preference-item group hover:scale-105 transition-all duration-300">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-lg border border-gray-200 dark:border-gray-600 hover:shadow-xl transition-all duration-300 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-purple-100 to-pink-200 dark:from-purple-900/20 dark:to-pink-800/20 rounded-full -translate-y-8 translate-x-8 opacity-60"></div>
                            <div class="flex items-center relative z-10">
                                <i data-lucide="heart" class="w-6 h-6 mr-4"></i>
                                <div class="flex-1">
                                    <p class="text-sm font-bold text-gray-900 dark:text-white mb-1">Style de voyage</p>
                                    <p class="text-base text-gray-700 dark:text-gray-300 font-semibold">${preferences.style}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            }

            if (preferences.budget) {
                items.push(`
                    <div class="preference-item group hover:scale-105 transition-all duration-300">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-lg border border-gray-200 dark:border-gray-600 hover:shadow-xl transition-all duration-300 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-amber-100 to-orange-200 dark:from-amber-900/20 dark:to-orange-800/20 rounded-full -translate-y-8 translate-x-8 opacity-60"></div>
                            <div class="flex items-center relative z-10">
                                <i data-lucide="euro" class="w-6 h-6 mr-4"></i>

                                <div class="flex-1">
                                    <p class="text-sm font-bold text-gray-900 dark:text-white mb-1">Budget</p>
                                    <p class="text-base text-gray-700 dark:text-gray-300 font-semibold">${preferences.budget}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            }

            if (preferences.travelers) {
                items.push(`
                    <div class="preference-item group hover:scale-105 transition-all duration-300">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-lg border border-gray-200 dark:border-gray-600 hover:shadow-xl transition-all duration-300 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-200 dark:from-indigo-900/20 dark:to-purple-800/20 rounded-full -translate-y-8 translate-x-8 opacity-60"></div>
                            <div class="flex items-center relative z-10">
                                <i data-lucide="users" class="w-6 h-6 mr-4"></i>
                                <div class="flex-1">
                                    <p class="text-sm font-bold text-gray-900 dark:text-white mb-1">Voyageurs</p>
                                    <p class="text-base text-gray-700 dark:text-gray-300 font-semibold">${preferences.travelers} personnes</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            }

            if (preferences.timing) {
                items.push(`
                    <div class="preference-item group hover:scale-105 transition-all duration-300">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-lg border border-gray-200 dark:border-gray-600 hover:shadow-xl transition-all duration-300 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-teal-100 to-cyan-200 dark:from-teal-900/20 dark:to-cyan-800/20 rounded-full -translate-y-8 translate-x-8 opacity-60"></div>
                            <div class="flex items-center relative z-10">
                                <i data-lucide="calendar" class="w-6 h-6 mr-4"></i>
                                <div class="flex-1">
                                    <p class="text-sm font-bold text-gray-900 dark:text-white mb-1">Timing</p>
                                    <p class="text-base text-gray-700 dark:text-gray-300 font-semibold">${preferences.timing}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            }

            return items.join('');
        }

        /**
         * Handle confirmation of preferences
         */
        async confirmPreferences() {
            try {
                // Show loading state
                this.showLoadingState();

                const response = await fetch(`${this.API_BASE_URL}/confirmation`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        preferences: this.preferences,
                        conversation_id: this.getCurrentConversationId(),
                        action: 'confirm'
                    })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    // Remove confirmation UI
                    this.removeConfirmationUI();

                    // Add confirmation message
                    this.addConfirmationMessage(data.message);

                    // Display offers if available
                    if (data.offers && data.offers.length > 0) {
                    // Use the existing displayOfferCards function from chat.js
                    if (typeof displayOfferCards === 'function') {
                        displayOfferCards(data.offers);
                    } else {
                        this.displayOffers(data.offers);
                    }
                    }
                } else {
                    this.showError('Failed to confirm preferences. Please try again.');
                }
            } catch (error) {
                console.error('Error confirming preferences:', error);
                this.showError('Network error. Please check your connection and try again.');
            } finally {
                this.hideLoadingState();
            }
        }

        /**
         * Handle modification of preferences
         */
        async modifyPreferences() {
            try {
                // Show loading state
                this.showLoadingState();

                const response = await fetch(`${this.API_BASE_URL}/confirmation`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        preferences: this.preferences,
                        conversation_id: this.getCurrentConversationId(),
                        action: 'modify'
                    })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    // Add modification message
                    this.addConfirmationMessage(data.message);

                    // Display offers if available
                    if (data.offers && data.offers.length > 0) {
                    // Use the existing displayOfferCards function from chat.js
                    if (typeof displayOfferCards === 'function') {
                        displayOfferCards(data.offers);
                    } else {
                        this.displayOffers(data.offers);
                    }
                    } else {
                        // If no offers returned, show error message
                        this.showError('Aucune offre trouvée pour vos critères. Veuillez essayer avec des préférences différentes.');
                    }
                } else {
                    this.showError('Failed to modify preferences. Please try again.');
                }
            } catch (error) {
                console.error('Error modifying preferences:', error);
                this.showError('Network error. Please check your connection and try again.');
                
                // Fallback: show error message
                this.showError('Erreur réseau. Veuillez vérifier votre connexion et réessayer.');
            } finally {
                this.hideLoadingState();
            }
        }



        /**
         * Display offers in a beautiful card layout
         */
        displayOffers(offers) {
        const chatArea = document.querySelector('.chat-messages');
            if (!chatArea) return;
            
            // Clear previous offers data
            this.offersData.clear();

            const offersHTML = `
                <div class="bg-white dark:bg-gray-800 shadow-2xl rounded-3xl rounded-bl-lg p-8 max-w-6xl border border-gray-100 dark:border-gray-700 backdrop-blur-sm relative overflow-hidden">
                <!-- Compact Header -->
                    <div class="text-center mb-6">
                    <div class="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full mb-4 animate-pulse">
                                                    <i data-lucide="gift" class="w-6 h-6"></i>
                    </div>
                    <h2 class="text-2xl font-bold text-mode-primary mb-2">Vos Offres Parfaites</h2>
                    <p class="text-base text-mode-secondary max-w-2xl mx-auto">
                            Voici les 3 meilleures offres sélectionnées spécialement pour vous selon vos préférences
                        </p>
                    </div>

                <!-- Compact Offers Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                    ${offers.map((offer, index) => this.createOfferCard(offer, index)).join('')}
                </div>

                <!-- Compact Footer -->
                <div class="text-center">
                    <div class="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 rounded-xl p-4 border border-gray-300 dark:border-gray-600">
                        <p class="text-sm font-medium text-gray-800 dark:text-gray-200">
                            <strong>Réservez en toute confiance :</strong> Toutes nos offres sont garanties et incluent une assistance 24/7
                        </p>
                    </div>
                    </div>
                </div>
            `;
            
        // Append the offers instead of replacing content
            chatArea.insertAdjacentHTML('beforeend', offersHTML);
        
        // Scroll to the new content
        const offersContainer = document.querySelector('.max-w-6xl.mx-auto.p-6.bg-mode-primary.rounded-2xl.shadow-medium.border.border-gray-300.dark\\:border-gray-600.animate-fade-in-up');
        if (offersContainer) {
            offersContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        // Refresh Lucide icons for the new content
            this.refreshLucideIcons();
        
    }

    /**
     * Create a beautiful offer card with enhanced JSON information
     */
    createOfferCard(offer, index) {
        const destinations = offer.destinations.map(d => `${d.city} (${d.country})`).join(', ');
        const highlights = offer.highlights.map(h => h.text).join(', ');
        
        // Use images from the dataset if available, otherwise fallback to destination-based images
        let imageUrl = '/assets/images/placeholder-travel.jpg';
        if (offer.images && offer.images.length > 0) {
            // Use the first image from the dataset
            imageUrl = offer.images[0];
        } else if (offer.destinations && offer.destinations.length > 0) {
            // Fallback to destination-based images
            const country = offer.destinations[0].country.toLowerCase();
            if (country.includes('japon') || country.includes('japan')) {
                imageUrl = 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&h=600&fit=crop';
            } else if (country.includes('thaïlande') || country.includes('thailand')) {
                imageUrl = 'https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800&h=600&fit=crop';
            } else if (country.includes('vietnam')) {
                imageUrl = 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=800&h=600&fit=crop';
            }
        }
        
        // Enhanced gradients with better colors
        const gradients = [
            'from-blue-500 via-purple-500 to-indigo-600',
            'from-emerald-500 via-teal-500 to-cyan-600', 
            'from-orange-500 via-red-500 to-pink-600',
            'from-purple-500 via-pink-500 to-rose-600',
            'from-teal-500 via-emerald-500 to-green-600'
        ];
        const gradient = gradients[index % gradients.length];
        
        // Staggered animation delay
        const animationDelay = index * 200;
        
        // Color coding for match percentage with vibrant colors for 90+
        const getMatchColor = (score) => {
            if (score >= 0.9) return 'from-blue-500 via-purple-500 to-pink-500';
            if (score >= 0.7) return 'from-emerald-500 to-green-600';
            if (score >= 0.5) return 'from-orange-500 to-amber-600';
            return 'from-red-500 to-pink-600';
        };
        
        // Get animation class for 90+ scores
        const getMatchAnimation = (score) => {
            if (score >= 0.9) return 'animate-pulse shadow-lg shadow-blue-400/50';
            return '';
        };
        
        // Add getMatchColor and getMatchAnimation methods to the class
        this.getMatchColor = getMatchColor;
        this.getMatchAnimation = getMatchAnimation;
        
        // Enhanced price range display based on offer type and group size
        const getPriceRange = (offer) => {
            if (offer.offer_type && offer.offer_type.toLowerCase().includes('luxe')) {
                return '€€€€€';
            } else if (offer.offer_type && offer.offer_type.toLowerCase().includes('premium')) {
                return '€€€€';
            } else {
                return '€€€';
            }
        };
        
        // Get group size information
        const getGroupSize = (offer) => {
            if (offer.min_group_size && offer.max_group_size) {
                if (offer.min_group_size === offer.max_group_size) {
                    return `${offer.min_group_size} personnes`;
                } else {
                    return `${offer.min_group_size}-${offer.max_group_size} personnes`;
                }
            } else if (offer.min_group_size) {
                return `${offer.min_group_size}+ personnes`;
            } else {
                return 'Petit groupe';
            }
        };
        
        // Get travel style from offer type
        const getTravelStyle = (offer) => {
            if (offer.offer_type) {
                return offer.offer_type;
            }
            return 'Premium';
        };
        
        // Get dates information
        const getDatesInfo = (offer) => {
            if (offer.dates && offer.dates.length > 0) {
                if (offer.dates.length === 1) {
                    return offer.dates[0];
                } else {
                    return `${offer.dates.length} dates disponibles`;
                }
            }
            return 'Dates flexibles';
        };
        
        // Store offer data in the Map instead of HTML attribute
        this.offersData.set(offer.reference, offer);
        
            return `
            <div class="offer-card group" 
                 style="animation-delay: ${animationDelay}ms;"
                 data-offer-reference="${offer.reference}">
                <div class="relative overflow-hidden">
                    <div class="absolute inset-0 bg-gradient-to-br ${gradient} opacity-10 group-hover:opacity-25 transition-opacity duration-500"></div>
                    <img src="${imageUrl}" alt="${offer.product_name}" class="offer-card-image" onerror="this.src='/assets/images/placeholder-travel.jpg'">
                    
                    <!-- Compact duration badge -->
                    <div class="absolute top-3 right-3">
                        <span class="offer-card-badge">
                            ${offer.duration} jours
                        </span>
                    </div>
                    
                    <!-- Compact rating -->
                    <div class="absolute bottom-3 left-3">
                        <div class="flex items-center offer-card-badge">
                            <div class="flex text-yellow-400 text-xs">
                                ${'★'.repeat(4)}${'☆'.repeat(1)}
                            </div>
                            <span class="text-xs text-gray-700 dark:text-gray-300 ml-1 font-bold">4.8</span>
                        </div>
                    </div>
                    
                    <!-- Compact ASIA Badge -->
                    <div class="absolute top-3 left-2">
                        <div class="bg-gradient-to-r from-error-500 to-error-600 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg border border-error-400/20 offer-card-badge">
                            ASIA
                        </div>
                    </div>
                    
                    <!-- Compact Match score badge with color coding -->
                    ${offer.match_score ? `
                        <div class="absolute bottom-3 right-3">
                            <div class="bg-gradient-to-r ${getMatchColor(offer.match_score)} ${getMatchAnimation(offer.match_score)} text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg border border-white/20 offer-card-badge"
                                 style="${offer.match_score >= 0.9 ? 'background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899) !important; animation: pulse 2s infinite;' : ''}">
                                ${Math.round(offer.match_score * 100)}%
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="offer-card-content">
                    <!-- Compact Title -->
                    <h3 class="font-bold text-lg text-mode-primary mb-3 line-clamp-2 hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-300 leading-tight">
                        ${offer.product_name}
                        </h3>
                    
                    <!-- Compact Destinations -->
                    <div class="flex items-center text-sm text-mode-secondary mb-3">
                        <div class="w-6 h-6 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mr-2">
                            <i data-lucide="map-pin" class="w-3 h-3"></i>
                        </div>
                        <span class="line-clamp-1 font-medium text-sm">${destinations}</span>
                    </div>
                    
                    <!-- Enhanced Departure and Dates -->
                    <div class="flex items-center text-sm text-mode-secondary mb-3">
                        <div class="w-6 h-6 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full flex items-center justify-center mr-2">
                            <i data-lucide="calendar" class="w-3 h-3"></i>
                        </div>
                        <span class="font-medium text-sm">Départ: ${offer.departure_city} • ${getDatesInfo(offer)}</span>
                    </div>
                    
                    <!-- Enhanced Group Size and Travel Style -->
                    <div class="flex items-center text-sm text-mode-secondary mb-3">
                        <div class="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center mr-2">
                            <i data-lucide="users" class="w-3 h-3"></i>
                        </div>
                        <span class="font-medium text-sm">${getGroupSize(offer)} • ${getTravelStyle(offer)}</span>
                    </div>
                    
                    <!-- Compact Description - Truncated -->
                    <p class="text-sm text-mode-tertiary mb-4 line-clamp-3 leading-relaxed">
                        ${offer.description && offer.description.length > 150 ? 
                            offer.description.substring(0, 150) + '...' : 
                            offer.description
                        }
                    </p>
                    
                    <!-- Enhanced Highlights (if available) - Truncated -->
                    ${offer.highlights && offer.highlights.length > 0 ? `
                        <div class="mb-4">
                            <div class="space-y-2">
                                ${offer.highlights.slice(0, 2).map(highlight => `
                                    <div class="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                                        <span class="font-medium text-gray-700 dark:text-gray-300">•</span> 
                                        ${(highlight.text || highlight).length > 120 ? 
                                            (highlight.text || highlight).substring(0, 120) + '...' : 
                                            (highlight.text || highlight)
                                        }
                                    </div>
                                `).join('')}
                                ${offer.highlights.length > 2 ? `
                                    <div class="text-xs text-gray-500 dark:text-gray-500 italic">
                                        +${offer.highlights.length - 2} autres points forts...
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                    
                    <!-- Match Score (simplified) -->
                    ${offer.match_score ? `
                        <div class="mb-4 flex items-center justify-between">
                            <span class="text-sm text-mode-secondary">Match:</span>
                            <div class="bg-gradient-to-r ${getMatchColor(offer.match_score)} ${getMatchAnimation(offer.match_score)} text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg border border-white/20 offer-card-badge"
                                 style="${offer.match_score >= 0.9 ? 'background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899) !important; animation: pulse 2s infinite;' : ''}">
                                ${Math.round(offer.match_score * 100)}%
                            </div>
                        </div>
                    ` : ''}
                    
                    <!-- Enhanced Action Buttons with forced red Réserver button -->
                    <div class="flex gap-2 justify-center pt-4 border-t border-gray-300 dark:border-gray-600 mt-auto">
                        <a href="${offer.price_url || '#'}" target="_blank" 
                           class="bg-red-600 hover:bg-red-700 text-white text-xs px-3 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg shadow-md font-bold flex items-center border border-red-500"
                           style="background: linear-gradient(to right, #dc2626, #b91c1c, #991b1b) !important;">
                            <i data-lucide="plus" class="w-3 h-3 mr-1 hover:animate-pulse"></i>
                            Réserver
                        </a>
                        <button onclick="window.confirmationFlow.showOfferDetails('${offer.reference}')" class="bg-gray-800 hover:bg-gray-900 text-white text-xs px-3 py-2 rounded-lg font-bold flex items-center justify-center border border-gray-700 transition-all duration-300 transform hover:scale-105 hover:shadow-lg shadow-md">
                            <i data-lucide="eye" class="w-3 h-3 mr-1 hover:animate-bounce"></i>
                            Détails
                        </button>
                    </div>
                    
                    <!-- Enhanced Price and Travel Type Info -->
                    <div class="text-center pt-2">
                        <div class="text-sm text-mode-secondary">
                            <span class="font-bold text-success-600 text-lg">${getPriceRange(offer)}</span>
                            <span class="ml-2 font-medium">${getGroupSize(offer)} • ${getTravelStyle(offer)}</span>
                        </div>
                    </div>
                    </div>
                </div>
            `;
        }

        /**
     * Format programme text into readable paragraphs
     */
    formatProgrammeText(text) {
        if (!text) return '<p>Programme détaillé non disponible</p>';
        
        // Split by common day patterns
        const lines = text.split('\n');
        let formattedHtml = '';
        let currentParagraph = '';
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Check if this is a day header (Jour X, Day X, etc.)
            if (line.match(/^(Jour|Day)\s+\d+/i) || line.match(/^Étape\s+\d+/i)) {
                // If we have accumulated content, close the previous paragraph
                if (currentParagraph) {
                    formattedHtml += `<p class="mb-4">${currentParagraph}</p>`;
                    currentParagraph = '';
                }
                
                // Add day header with special styling
                formattedHtml += `<h4 class="font-bold text-lg text-blue-600 dark:text-blue-400 mb-3 mt-6 first:mt-0">${line}</h4>`;
            }
            // Check if this is a meal indicator
            else if (line.match(/\([A-Za-z\.]+\)/)) {
                if (currentParagraph) {
                    currentParagraph += ' ';
                }
                currentParagraph += `<span class="font-semibold text-emerald-600 dark:text-emerald-400">${line}</span>`;
            }
            // Check if this is an empty line (paragraph break)
            else if (line === '') {
                if (currentParagraph) {
                    formattedHtml += `<p class="mb-4">${currentParagraph}</p>`;
                    currentParagraph = '';
                }
            }
            // Regular content
            else if (line) {
                if (currentParagraph) {
                    currentParagraph += ' ';
                }
                currentParagraph += line;
            }
        }
        
        // Add any remaining content
        if (currentParagraph) {
            formattedHtml += `<p class="mb-4">${currentParagraph}</p>`;
        }
        
        return formattedHtml || `<p>${text}</p>`;
    }



    /**
     * Show offer details modal - Full screen with map and details
         */
        showOfferDetails(offerReference) {
            console.log('🔍 Opening modal for offer:', offerReference);
            
            // Remove any existing modals first
            const existingModals = document.querySelectorAll('.offer-details-modal');
            existingModals.forEach(modal => modal.remove());
            
        // Get offer data from the Map instead of HTML attributes
            const offerData = this.offersData.get(offerReference);
            
            if (!offerData) {
                console.error('❌ No offer data found for reference:', offerReference);
                return;
            }
            
        console.log('✅ Offer data found:', offerData);
        
        // Get destinations for map
        const destinations = offerData?.destinations || [];
        const firstDestination = destinations[0] || { city: 'Tokyo', country: 'Japon' };
        
        // Generate map URL based on destination
        const mapUrl = this.generateMapUrl(firstDestination);
            
            const modal = document.createElement('div');
            modal.className = 'offer-details-modal fixed inset-0 bg-black/95 flex items-center justify-center z-50 backdrop-blur-md';
        modal.innerHTML = `
            <div class="w-full h-full flex flex-col lg:flex-row bg-white dark:bg-gray-900 relative overflow-hidden">
                <!-- Background Pattern -->
                <div class="absolute inset-0 opacity-5">
                    <div class="absolute top-10 left-10 w-32 h-32 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur-3xl"></div>
                    <div class="absolute bottom-10 right-10 w-40 h-40 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full blur-3xl"></div>
                    <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-60 h-60 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full blur-3xl"></div>
                </div>
                
                <!-- Close button -->
                <button onclick="this.closest('.offer-details-modal').remove()" class="absolute top-6 right-6 z-50 bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white rounded-full p-4 transition-all duration-300 shadow-lg border border-white/20">
                    <i data-lucide="x" class="w-6 h-6"></i>
                </button>
                
                <!-- Left side - Enhanced Map -->
                <div class="w-full lg:w-1/2 h-1/2 lg:h-full relative bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-800 dark:to-gray-900 overflow-hidden">
                    <!-- Map Header -->
                    <div class="absolute top-0 left-0 right-0 z-20 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 p-4">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center space-x-3">
                                <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white">
                                        <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path>
                                        <circle cx="12" cy="10" r="3"></circle>
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="font-bold text-gray-900 dark:text-white">Itinéraire du Voyage</h3>
                                    <p class="text-sm text-gray-600 dark:text-gray-400">${destinations.length} destinations</p>
                                </div>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-xs font-medium">
                                    ${offerData?.duration || 14} jours
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Working Google Maps with Route Visualization -->
                    <div class="absolute inset-0 pt-20 pb-4 px-4">
                        <div class="relative w-full h-full bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800 rounded-2xl border border-gray-200 dark:border-gray-600 shadow-xl overflow-hidden">
                            
                            <!-- Google Maps iframe -->
                            <iframe 
                                src="${mapUrl}" 
                                class="w-full h-full border-0 rounded-2xl" 
                                style="filter: grayscale(20%) contrast(110%);"
                                allowfullscreen 
                                loading="lazy" 
                                referrerpolicy="no-referrer-when-downgrade">
                            </iframe>
                            
                            <!-- Overlay with route information -->
                            <div class="absolute top-4 left-4 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-600 shadow-lg">
                                <div class="flex items-center space-x-3 mb-3">
                                    <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                                        <i data-lucide="route" class="w-4 h-4 text-white"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-bold text-gray-900 dark:text-white">Itinéraire</h4>
                                        <p class="text-sm text-gray-600 dark:text-gray-400">${destinations.length} destinations</p>
                                    </div>
                                </div>
                                
                                <!-- Route summary -->
                                <div class="space-y-2">
                                    ${destinations.map((dest, index) => `
                                        <div class="flex items-center space-x-2">
                                            <div class="w-6 h-6 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                                                <span class="text-xs font-bold text-white">${index + 1}</span>
                                            </div>
                                            <div class="text-sm">
                                                <span class="font-medium text-gray-900 dark:text-white">${dest.city}</span>
                                                <span class="text-gray-500 dark:text-gray-400">, ${dest.country}</span>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            
                            <!-- Map controls overlay -->
                            <div class="absolute bottom-4 right-4 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl p-3 border border-gray-200 dark:border-gray-600 shadow-lg">
                                <div class="flex items-center space-x-2">
                                    <button class="w-8 h-8 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center justify-center transition-colors duration-200">
                                        <i data-lucide="maximize" class="w-4 h-4"></i>
                                    </button>
                                    <button class="w-8 h-8 bg-gray-500 hover:bg-gray-600 text-white rounded-lg flex items-center justify-center transition-colors duration-200">
                                        <i data-lucide="navigation" class="w-4 h-4"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Right side - Enhanced Offer Details -->
                <div class="w-full lg:w-1/2 h-1/2 lg:h-full overflow-y-auto bg-white dark:bg-gray-900 relative pb-32">
                    <!-- Content Container -->
                    <div class="p-6 lg:p-8 relative z-10">
                        <!-- Enhanced Header -->
                        <div class="mb-8">
                            <div class="flex items-center justify-between mb-6">
                                <div class="flex items-center space-x-4">
                                    <div class="w-16 h-16 bg-gradient-to-r from-blue-500 via-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl">
                                        <i data-lucide="plane" class="w-8 h-8 text-white"></i>
                                    </div>
                                    <div>
                                        <h1 class="text-3xl lg:text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">${offerData?.product_name || 'Offre de voyage'}</h1>
                                        <div class="flex items-center space-x-4 mt-2">
                                            <p class="text-sm text-gray-500 dark:text-gray-400">Référence: ${offerReference}</p>
                                            ${offerData?.match_score ? `
                                                <div class="text-white text-sm px-3 py-1 rounded-full font-bold shadow-lg border border-white/20"
                                                     style="background: linear-gradient(to right, ${offerData.match_score >= 0.9 ? '#3b82f6, #8b5cf6, #ec4899' : offerData.match_score >= 0.7 ? '#10b981, #059669' : offerData.match_score >= 0.5 ? '#f59e0b, #d97706' : '#ef4444, #dc2626'}); ${offerData.match_score >= 0.9 ? 'animation: pulse 2s infinite;' : ''}">
                                                    Match: ${Math.round(offerData.match_score * 100)}%
                                                </div>
                                            ` : ''}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                                                <!-- Enhanced Quick stats with better design -->
                    <div class="grid grid-cols-3 gap-6 mb-10">
                        <div class="group relative">
                            <div class="bg-gradient-to-br from-blue-50 via-blue-100 to-indigo-50 dark:from-blue-900/30 dark:via-blue-800/20 dark:to-indigo-900/30 rounded-3xl p-6 text-center border-2 border-blue-200 dark:border-blue-700/50 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2">
                                <div class="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                                <div class="relative z-10">
                                    <div class="text-4xl font-black text-blue-600 dark:text-blue-400 mb-2 group-hover:scale-110 transition-transform duration-300">${offerData?.duration || 14}</div>
                                    <div class="text-sm text-gray-700 dark:text-gray-300 font-semibold uppercase tracking-wide">Jours</div>
                                </div>
                            </div>
                        </div>
                        <div class="group relative">
                            <div class="bg-gradient-to-br from-emerald-50 via-emerald-100 to-teal-50 dark:from-emerald-900/30 dark:via-emerald-800/20 dark:to-teal-900/30 rounded-3xl p-6 text-center border-2 border-emerald-200 dark:border-emerald-700/50 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2">
                                <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-teal-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                                <div class="relative z-10">
                                    <div class="text-4xl font-black text-emerald-600 dark:text-emerald-400 mb-2 group-hover:scale-110 transition-transform duration-300">${destinations.length}</div>
                                    <div class="text-sm text-gray-700 dark:text-gray-300 font-semibold uppercase tracking-wide">Destinations</div>
                                </div>
                            </div>
                        </div>
                        <div class="group relative">
                            <div class="bg-gradient-to-br from-purple-50 via-purple-100 to-pink-50 dark:from-purple-900/30 dark:via-purple-800/20 dark:to-pink-900/30 rounded-3xl p-6 text-center border-2 border-purple-200 dark:border-purple-700/50 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2">
                                <div class="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                                <div class="relative z-10">
                                    <div class="text-4xl font-black text-purple-600 dark:text-purple-400 mb-2 group-hover:scale-110 transition-transform duration-300">${offerData?.match_score ? Math.round(offerData.match_score * 100) : 'N/A'}</div>
                                    <div class="text-sm text-gray-700 dark:text-gray-300 font-semibold uppercase tracking-wide">Match %</div>
                                </div>
                            </div>
                        </div>
                    </div>
                        </div>
                    
                    <!-- Enhanced Description Section with Full Dataset Information -->
                    <div class="mb-10">
                        <div class="flex items-center mb-6">
                            <div class="w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full mr-4"></div>
                            <h2 class="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">Description Complète</h2>
                        </div>
                        
                        <div class="bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 dark:from-gray-800 dark:via-blue-900/20 dark:to-indigo-900/20 rounded-3xl p-8 border-2 border-blue-200/50 dark:border-blue-700/30 shadow-xl">
                            <div class="relative">
                                <!-- Decorative elements -->
                                <div class="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-200 dark:from-blue-800/30 dark:to-indigo-700/30 rounded-full -translate-y-10 translate-x-10 opacity-60"></div>
                                
                                <div class="relative z-10">
                                    <p class="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-8 font-medium">${offerData?.description || 'Description détaillée de cette offre de voyage exceptionnelle.'}</p>
                                    
                                    <!-- Programme complet -->
                                    ${offerData?.programme ? `
                                        <div class="mb-8">
                                            <h3 class="font-bold text-gray-900 dark:text-white mb-4 flex items-center text-lg">
                                                <div class="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl flex items-center justify-center mr-3">
                                                    <i data-lucide="book-open" class="w-5 h-5 text-white"></i>
                                                </div>
                                                Programme Complet
                                            </h3>
                                            <div class="bg-white/80 dark:bg-gray-700/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 dark:border-gray-600/50">
                                                <div class="text-gray-700 dark:text-gray-300 leading-relaxed space-y-4">
                                                    ${this.formatProgrammeText(offerData.programme)}
                                                </div>
                                            </div>
                                        </div>
                                    ` : ''}
                                    
                                    <!-- Enhanced Additional details -->
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div class="group bg-white/80 dark:bg-gray-700/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 dark:border-gray-600/50 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                                            <h3 class="font-bold text-gray-900 dark:text-white mb-3 flex items-center text-lg">
                                                <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center mr-3">
                                                    <i data-lucide="calendar" class="w-5 h-5 text-white"></i>
                                                </div>
                                                Dates de Voyage
                                            </h3>
                                            <p class="text-gray-600 dark:text-gray-300 font-medium">${offerData?.dates ? offerData.dates.join(', ') : 'Dates flexibles selon disponibilité'}</p>
                                        </div>
                                        
                                        <div class="group bg-white/80 dark:bg-gray-700/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 dark:border-gray-600/50 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                                            <h3 class="font-bold text-gray-900 dark:text-white mb-3 flex items-center text-lg">
                                                <div class="w-10 h-10 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center mr-3">
                                                    <i data-lucide="users" class="w-5 h-5 text-white"></i>
                                                </div>
                                                Taille du Groupe
                                            </h3>
                                            <p class="text-gray-600 dark:text-gray-300 font-medium">${offerData?.min_group_size ? `${offerData.min_group_size}-${offerData.max_group_size} personnes` : 'Petit groupe (max 12 personnes)'}</p>
                                        </div>
                                        
                                        <div class="group bg-white/80 dark:bg-gray-700/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 dark:border-gray-600/50 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                                            <h3 class="font-bold text-gray-900 dark:text-white mb-3 flex items-center text-lg">
                                                <div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mr-3">
                                                    <i data-lucide="map-pin" class="w-5 h-5 text-white"></i>
                                                </div>
                                                Ville de Départ
                                            </h3>
                                            <p class="text-gray-600 dark:text-gray-300 font-medium">${offerData?.departure_city || 'Paris'}</p>
                                        </div>
                                        
                                        <div class="group bg-white/80 dark:bg-gray-700/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 dark:border-gray-600/50 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                                            <h3 class="font-bold text-gray-900 dark:text-white mb-3 flex items-center text-lg">
                                                <div class="w-10 h-10 bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl flex items-center justify-center mr-3">
                                                    <i data-lucide="star" class="w-5 h-5 text-white"></i>
                                                </div>
                                                Type d'Offre
                                            </h3>
                                            <p class="text-gray-600 dark:text-gray-300 font-medium">${offerData?.offer_type || 'Premium - Culture et Découverte'}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Fixed and Enhanced Destinations Timeline -->
                    <div class="mb-10">
                        <div class="flex items-center mb-8">
                            <div class="w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full mr-4"></div>
                            <h2 class="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">Itinéraire du Voyage</h2>
                        </div>
                        
                        <div class="relative bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 rounded-3xl p-8 border-2 border-blue-200/50 dark:border-blue-700/30 shadow-xl">
                            <!-- Fixed Timeline line with better positioning -->
                            <div class="absolute left-12 top-12 bottom-12 w-2 bg-gradient-to-b from-blue-500 via-purple-500 to-emerald-500 rounded-full shadow-lg"></div>
                            
                            <!-- Destination stations with better layout -->
                            <div class="space-y-24">
                                ${destinations.map((dest, index) => `
                                    <div class="relative flex items-start group mb-8">
                                        <!-- Fixed Destination card with better layout -->
                                        <div class="flex-1 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-gray-200/50 dark:border-gray-600/50 hover:shadow-2xl transition-all duration-500 transform group-hover:-translate-y-1">
                                            <div class="flex items-center justify-between mb-4">
                                                <div class="flex-1">
                                                    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">${dest.city}</h3>
                                                    <p class="text-lg text-gray-500 dark:text-gray-400 font-medium">${dest.country}</p>
                                                </div>
                                                <div class="text-right ml-4">
                                                    <span class="text-sm text-gray-400 dark:text-gray-500 font-medium">Étape ${index + 1}</span>
                                                    ${index > 0 ? `<div class="text-lg text-blue-600 dark:text-blue-400 mt-2 font-bold">+${Math.floor(Math.random() * 3) + 1}h</div>` : ''}
                                                </div>
                                            </div>
                                            
                                            <!-- Fixed Destination highlights with better spacing -->
                                            <div class="flex flex-wrap gap-4 mt-6">
                                                <span class="inline-flex items-center px-4 py-3 rounded-full text-base font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border-2 border-blue-200 dark:border-blue-700/30 hover:bg-blue-200 dark:hover:bg-blue-800/40 transition-colors duration-200">
                                                    <i data-lucide="camera" class="w-5 h-5 mr-3"></i>
                                                    Photos
                                                </span>
                                                <span class="inline-flex items-center px-4 py-3 rounded-full text-base font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 border-2 border-green-200 dark:border-green-700/30 hover:bg-green-200 dark:hover:bg-green-800/40 transition-colors duration-200">
                                                    <i data-lucide="utensils" class="w-5 h-5 mr-3"></i>
                                                    Gastronomie
                                                </span>
                                                <span class="inline-flex items-center px-4 py-3 rounded-full text-base font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 border-2 border-purple-200 dark:border-purple-700/30 hover:bg-purple-200 dark:hover:bg-purple-800/40 transition-colors duration-200">
                                                    <i data-lucide="landmark" class="w-5 h-5 mr-3"></i>
                                                    Culture
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Enhanced Images Gallery -->
                    ${offerData?.images && offerData.images.length > 0 ? `
                        <div class="mb-10">
                            <div class="flex items-center mb-8">
                                <div class="w-1 h-8 bg-gradient-to-b from-pink-500 to-rose-600 rounded-full mr-4"></div>
                                <h2 class="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">Galerie Photos</h2>
                            </div>
                            
                            <div class="bg-gradient-to-br from-pink-50 via-rose-50 to-red-50 dark:from-pink-900/20 dark:via-rose-900/20 dark:to-red-900/20 rounded-3xl p-8 border-2 border-pink-200/50 dark:border-pink-700/30 shadow-xl">
                                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    ${offerData.images.map((image, index) => `
                                        <div class="group relative overflow-hidden rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2">
                                            <img src="${image}" alt="Photo ${index + 1}" 
                                                 class="w-full h-56 object-cover group-hover:scale-110 transition-transform duration-700"
                                                 onerror="this.src='https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop'">
                                            <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                                            <div class="absolute bottom-0 left-0 right-0 p-6 text-white transform translate-y-full group-hover:translate-y-0 transition-transform duration-500">
                                                <p class="text-lg font-bold mb-1">Photo ${index + 1}</p>
                                                <p class="text-sm opacity-90">Cliquez pour agrandir</p>
                                            </div>
                                            
                                            <!-- Image number badge -->
                                            <div class="absolute top-4 right-4 w-8 h-8 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg">
                                                <span class="text-sm font-bold text-gray-900 dark:text-white">${index + 1}</span>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    ` : `
                        <!-- Enhanced Placeholder images -->
                        <div class="mb-10">
                            <div class="flex items-center mb-8">
                                <div class="w-1 h-8 bg-gradient-to-b from-pink-500 to-rose-600 rounded-full mr-4"></div>
                                <h2 class="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">Galerie Photos</h2>
                            </div>
                            
                            <div class="bg-gradient-to-br from-pink-50 via-rose-50 to-red-50 dark:from-pink-900/20 dark:via-rose-900/20 dark:to-red-900/20 rounded-3xl p-8 border-2 border-pink-200/50 dark:border-pink-700/30 shadow-xl">
                                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    ${this.generateDestinationImages(destinations).map((image, index) => `
                                        <div class="group relative overflow-hidden rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2">
                                            <img src="${image}" alt="Photo ${index + 1}" 
                                                 class="w-full h-56 object-cover group-hover:scale-110 transition-transform duration-700">
                                            <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                                            <div class="absolute bottom-0 left-0 right-0 p-6 text-white transform translate-y-full group-hover:translate-y-0 transition-transform duration-500">
                                                <p class="text-lg font-bold mb-1">${destinations[index] ? destinations[index].city : 'Destination'}</p>
                                                <p class="text-sm opacity-90">Cliquez pour agrandir</p>
                                            </div>
                                            
                                            <!-- Image number badge -->
                                            <div class="absolute top-4 right-4 w-8 h-8 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg">
                                                <span class="text-sm font-bold text-gray-900 dark:text-white">${index + 1}</span>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    `}
                    
                    <!-- Services Inclus et Non Inclus -->
                    <div class="mb-8">
                        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Services Inclus & Non Inclus</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Services Inclus -->
                            <div class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6">
                                <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                                    <i data-lucide="check-circle" class="w-6 h-6 text-green-600 dark:text-green-400 mr-2"></i>
                                    Services Inclus
                                </h3>
                                ${offerData?.included && offerData.included.length > 0 ? `
                                    <div class="space-y-4">
                                        ${offerData.included.map(item => `
                                            <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                                <i data-lucide="check" class="w-4 h-4 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                                <span class="text-gray-700 dark:text-gray-300 text-sm">${item}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                ` : `
                                    <div class="space-y-4">
                                        <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                            <i data-lucide="check" class="w-4 h-4 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm">Hébergement en hôtels sélectionnés</span>
                                        </div>
                                        <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                            <i data-lucide="check" class="w-4 h-4 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm">Transport privé avec chauffeur</span>
                                        </div>
                                        <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                            <i data-lucide="check" class="w-4 h-4 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm">Guide local francophone</span>
                                        </div>
                                    </div>
                                `}
                            </div>
                            
                            <!-- Services Non Inclus -->
                            <div class="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-xl p-6">
                                <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                                    <i data-lucide="x-circle" class="w-6 h-6 text-red-600 dark:text-red-400 mr-2"></i>
                                    Services Non Inclus
                                </h3>
                                ${offerData?.not_included && offerData.not_included.length > 0 ? `
                                    <div class="space-y-4">
                                        ${offerData.not_included.map(item => `
                                            <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-red-200 dark:border-red-700/30">
                                                <i data-lucide="x" class="w-4 h-4 text-red-600 dark:text-red-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                                <span class="text-gray-700 dark:text-gray-300 text-sm">${item}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                ` : `
                                    <div class="space-y-4">
                                        <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-red-200 dark:border-red-700/30">
                                            <i data-lucide="x" class="w-4 h-4 text-red-600 dark:text-red-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm">Vols internationaux</span>
                                        </div>
                                        <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-red-200 dark:border-red-700/30">
                                            <i data-lucide="x" class="w-4 h-4 text-red-600 dark:text-red-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm">Assurance voyage</span>
                                        </div>
                                        <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-red-200 dark:border-red-700/30">
                                            <i data-lucide="x" class="w-4 h-4 text-red-600 dark:text-red-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm">Dépenses personnelles</span>
                                        </div>
                                    </div>
                                `}
                            </div>
                        </div>
                    </div>

                    <!-- Informations Pratiques -->
                    ${offerData?.practical_info ? `
                        <div class="mb-8">
                            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Informations Pratiques</h2>
                            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6">
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    ${Object.entries(offerData.practical_info).map(([key, value]) => `
                                        <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-blue-200 dark:border-blue-700/30">
                                            <i data-lucide="info" class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                            <div>
                                                <h4 class="font-semibold text-gray-900 dark:text-white text-sm mb-1">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                                                <p class="text-gray-700 dark:text-gray-300 text-sm">${value}</p>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    ` : ''}

                    <!-- Highlights -->
                    <div class="mb-8">
                        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Points Forts & Expériences</h2>
                        <div class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6">
                            ${offerData?.highlights && offerData.highlights.length > 0 ? `
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                    ${offerData.highlights.map(highlight => `
                                        <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                            <i data-lucide="check-circle" class="w-5 h-5 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                            <div>
                                                <span class="text-gray-700 dark:text-gray-300 text-sm font-medium">${highlight.text}</span>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : `
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                        <i data-lucide="check-circle" class="w-5 h-5 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                        <div>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm font-medium">Guide local francophone</span>
                                        </div>
                                    </div>
                                    <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                        <i data-lucide="check-circle" class="w-5 h-5 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                        <div>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm font-medium">Hébergements de qualité</span>
                                        </div>
                                    </div>
                                    <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                        <i data-lucide="check-circle" class="w-5 h-5 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                        <div>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm font-medium">Transport privé inclus</span>
                                        </div>
                                    </div>
                                    <div class="flex items-start p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-700/30">
                                        <i data-lucide="check-circle" class="w-5 h-5 text-green-600 dark:text-green-400 mr-3 mt-0.5 flex-shrink-0"></i>
                                        <div>
                                            <span class="text-gray-700 dark:text-gray-300 text-sm font-medium">Expériences authentiques</span>
                                        </div>
                                    </div>
                                </div>
                            `}
                            
                            <!-- Additional experiences -->
                            <div class="mt-6 pt-6 border-t border-green-200 dark:border-green-700/30">
                                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Expériences Incluses</h3>
                                <div class="flex flex-row gap-4 justify-center">
                                    <div class="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                                        <i data-lucide="utensils" class="w-8 h-8 text-orange-600 dark:text-orange-400 mx-auto mb-2"></i>
                                        <p class="text-sm text-gray-700 dark:text-gray-300">Dégustations culinaires</p>
                                    </div>
                                    <div class="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                                        <i data-lucide="landmark" class="w-8 h-8 text-purple-600 dark:text-purple-400 mx-auto mb-2"></i>
                                        <p class="text-sm text-gray-700 dark:text-gray-300">Sites culturels</p>
                                    </div>
                                    <div class="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                                        <i data-lucide="camera" class="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto mb-2"></i>
                                        <p class="text-sm text-gray-700 dark:text-gray-300">Photos souvenirs</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- AI Reasoning -->
                    ${offerData?.ai_reasoning ? `
                        <div class="mb-8">
                            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Pourquoi cette offre vous convient</h2>
                            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6">
                                <div class="flex items-start">
                                    <i data-lucide="brain" class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3 mt-1 flex-shrink-0"></i>
                                    <p class="text-gray-700 dark:text-gray-300 leading-relaxed">${offerData.ai_reasoning}</p>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    
                    <!-- Match Score -->
                    ${offerData?.match_score ? `
                        <div class="mb-8">
                            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Score de correspondance</h2>
                            <div class="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-6">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center">
                                        <i data-lucide="target" class="w-6 h-6 text-purple-600 dark:text-purple-400 mr-3"></i>
                                        <span class="text-gray-700 dark:text-gray-300 font-medium">Correspondance avec vos préférences</span>
                                    </div>
                                    <div class="bg-gradient-to-r ${this.getMatchColor(offerData.match_score)} ${this.getMatchAnimation(offerData.match_score)} text-white text-lg px-4 py-2 rounded-full font-bold shadow-lg border border-white/20"
                                         style="${offerData.match_score >= 0.9 ? 'background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899) !important; animation: pulse 2s infinite;' : ''}">
                                        ${Math.round(offerData.match_score * 100)}%
                                    </div>
                                </div>
                                <div class="mt-4 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                                    <div class="bg-gradient-to-r ${this.getMatchColor(offerData.match_score)} ${this.getMatchAnimation(offerData.match_score)} h-3 rounded-full transition-all duration-1000" 
                                         style="width: ${offerData.match_score * 100}%; ${offerData.match_score >= 0.9 ? 'background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899) !important; animation: pulse 2s infinite;' : ''}"></div>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    
                    <!-- Enhanced Action buttons with forced red background -->
                    <div class="fixed bottom-0 left-1/2 right-0 bg-white dark:bg-gray-900 pt-6 border-t border-gray-200 dark:border-gray-700 z-10">
                        <div class="flex flex-col sm:flex-row gap-4">
                            <a href="${offerData?.price_url || '#'}" target="_blank" 
                               class="flex-1 bg-red-600 hover:bg-red-700 text-white px-8 py-5 rounded-2xl font-bold text-xl transition-all duration-300 transform hover:scale-105 hover:shadow-2xl shadow-xl flex items-center justify-center group relative overflow-hidden"
                               style="background: linear-gradient(to right, #dc2626, #b91c1c, #991b1b) !important; border: 2px solid #dc2626 !important;">
                                <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                                <i data-lucide="credit-card" class="w-6 h-6 mr-3 relative z-10 group-hover:animate-pulse text-white"></i>
                                <span class="relative z-10 text-white">Réserver maintenant</span>
                            </a>
                            <button onclick="this.closest('.offer-details-modal').remove()" 
                                    class="flex-1 px-8 py-5 bg-gradient-to-r from-gray-900 via-black to-gray-900 hover:from-black hover:via-gray-900 hover:to-black text-white border-2 border-gray-700 dark:border-gray-600 rounded-2xl transition-all duration-300 hover:shadow-2xl shadow-xl font-bold text-lg">
                                Annuler
                            </button>
                        </div>
                    </div>
                </div>
                </div>
            </div>
        `;
            document.body.appendChild(modal);
        
        // Refresh Lucide icons for the modal
            this.refreshLucideIcons();
        
        console.log('✅ Modal created and added to document');
            
            // Add click outside to close
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
        }

        /**
         * Generate map URL based on destination
         */
        generateMapUrl(destination) {
            const city = encodeURIComponent(destination.city);
            const country = encodeURIComponent(destination.country);
            return `https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${city},${country}&zoom=12`;
        }
    
    /**
     * Generate destination-specific images
     */
    generateDestinationImages(destinations) {
        const imageUrls = [];
        
        destinations.forEach((dest, index) => {
            const country = dest.country.toLowerCase();
            const city = dest.city.toLowerCase();
            
            // Japan images
            if (country.includes('japon') || country.includes('japan') || country.includes('jp')) {
                if (city.includes('tokyo')) {
                    imageUrls.push('https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop');
                } else if (city.includes('kyoto')) {
                    imageUrls.push('https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop');
                } else if (city.includes('osaka')) {
                    imageUrls.push('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop');
                } else {
                    imageUrls.push('https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop');
                }
            }
            // Thailand images
            else if (country.includes('thaïlande') || country.includes('thailand') || country.includes('th')) {
                if (city.includes('bangkok')) {
                    imageUrls.push('https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=400&h=300&fit=crop');
                } else if (city.includes('phuket')) {
                    imageUrls.push('https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=400&h=300&fit=crop');
                } else {
                    imageUrls.push('https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=400&h=300&fit=crop');
                }
            }
            // Vietnam images
            else if (country.includes('vietnam') || country.includes('vn')) {
                if (city.includes('hanoï') || city.includes('hanoi')) {
                    imageUrls.push('https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=400&h=300&fit=crop');
                } else if (city.includes('ho chi minh')) {
                    imageUrls.push('https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop');
                } else {
                    imageUrls.push('https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=400&h=300&fit=crop');
                }
            }
            // China images
            else if (country.includes('chine') || country.includes('china') || country.includes('cn')) {
                if (city.includes('beijing') || city.includes('pékin')) {
                    imageUrls.push('https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop');
                } else if (city.includes('shanghai')) {
                    imageUrls.push('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop');
                } else {
                    imageUrls.push('https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop');
                }
            }
            // Default images for other destinations
            else {
                const defaultImages = [
                    'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop',
                    'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop',
                    'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop',
                    'https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=400&h=300&fit=crop',
                    'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=400&h=300&fit=crop'
                ];
                imageUrls.push(defaultImages[index % defaultImages.length]);
            }
        });
        
        // Ensure we have at least 3 images
        while (imageUrls.length < 3) {
            imageUrls.push('https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop');
        }
        
        return imageUrls.slice(0, 6); // Return max 6 images
    }

    /**
     * Book offer (placeholder)
     */
    bookOffer(offerReference) {
        alert(`Réservation pour l'offre ${offerReference} - Cette fonctionnalité sera bientôt disponible!`);
        }

        /**
         * Helper methods
         */
        getCurrentConversationId() {
            const urlParams = new URLSearchParams(window.location.search);
            const convId = urlParams.get('conversation_id');
            
            if (convId) {
                return convId;
            }
            
            const pathParts = window.location.pathname.split('/');
            const conversationIdFromPath = pathParts[pathParts.length - 1];
            
            if (conversationIdFromPath && !isNaN(conversationIdFromPath)) {
                return conversationIdFromPath;
            }
            
            return 'conv_' + Date.now();
        }

        showLoadingState() {
            // Add loading overlay
            const overlay = document.createElement('div');
        overlay.id = 'confirmation-loading';
        overlay.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
            overlay.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-xl p-6 flex items-center space-x-4">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span class="text-gray-900 dark:text-white">Processing your request...</span>
                </div>
            `;
            document.body.appendChild(overlay);
        }

        hideLoadingState() {
        const overlay = document.getElementById('confirmation-loading');
            if (overlay) {
                overlay.remove();
            }
        }

        removeConfirmationUI() {
        // Remove all confirmation-related elements
        document.querySelectorAll('.confirmation-ui').forEach(el => el.remove());
        }

        addConfirmationMessage(message) {
        const chatArea = document.querySelector('.chat-messages');
            if (!chatArea) return;

            const messageDiv = document.createElement('div');
            messageDiv.className = 'flex justify-start mb-6';
            messageDiv.innerHTML = `
            <div class="bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl">
                <p class="text-gray-800 dark:text-white/90 font-normal">${message}</p>
                </div>
            `;
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        showError(message) {
        const chatArea = document.querySelector('.chat-messages');
            if (!chatArea) return;

            const errorDiv = document.createElement('div');
            errorDiv.className = 'flex justify-start mb-6';
            errorDiv.innerHTML = `
            <div class="bg-red-100 dark:bg-red-500 text-red-700 dark:text-white rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl">
                <p class="font-normal">${message}</p>
                </div>
            `;
            chatArea.appendChild(errorDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

            // Initialize the confirmation flow
    init() {
        // Initialize dark mode colors
        this.updateDarkModeColors();
        
        console.log('ConfirmationFlow initialized');
        
        // Ensure Lucide icons are initialized after DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeLucideIcons();
            });
        } else {
            // DOM is already loaded
            setTimeout(() => {
                this.initializeLucideIcons();
            }, 100);
        }
    }

    /**
     * Update dark mode colors for dynamic elements
     */
    updateDarkModeColors() {
        const isDarkMode = this.getCurrentMode() === 'dark';
        
        // Update CSS custom properties for dark mode
        if (isDarkMode) {
            document.documentElement.style.setProperty('--text-mode-primary', '#f9fafb');
            document.documentElement.style.setProperty('--text-mode-secondary', '#d1d5db');
            document.documentElement.style.setProperty('--text-mode-tertiary', '#9ca3af');
        } else {
            document.documentElement.style.setProperty('--text-mode-primary', '#1f2937');
            document.documentElement.style.setProperty('--text-mode-secondary', '#6b7280');
            document.documentElement.style.setProperty('--text-mode-tertiary', '#9ca3af');
        }
    }


}

// Initialize the confirmation flow
const confirmationFlow = new ConfirmationFlow();
confirmationFlow.init();

// Make it available globally
window.confirmationFlow = confirmationFlow; 