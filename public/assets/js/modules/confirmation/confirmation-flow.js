/**
 * Confirmation Flow Module for ASIA.fr Agent Frontend
 */

// Only create if not already defined
if (typeof ConfirmationFlow === 'undefined') {
    class ConfirmationFlow {
        constructor() {
            this.API_BASE_URL = window.UnifiedConfig ? window.UnifiedConfig.getApiBaseUrl() : 'http://localhost:8000';
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
            return isDarkMode ? 'light' : 'dark';
        }

        /**
         * Display confirmation request with user preferences
         */
        displayConfirmationRequest(preferences, confirmationSummary) {
            const chatArea = document.querySelector('.p-5.py-12');
            if (!chatArea) return;

            // Use Twig template for rendering
            const confirmationHtml = this.renderConfirmationTemplate(preferences);
            
            const confirmationDiv = document.createElement('div');
            confirmationDiv.className = 'flex justify-start mb-6 animate-fade-in';
            confirmationDiv.innerHTML = confirmationHtml;

            chatArea.appendChild(confirmationDiv);
            chatArea.scrollTop = chatArea.scrollHeight;

            // Store current preferences
            this.preferences = preferences;
            
            // Refresh Lucide icons for the new content
            this.refreshLucideIcons();
        }

        /**
         * Render confirmation template using Twig-like structure
         */
        renderConfirmationTemplate(preferences) {
            // This would be replaced with actual Twig template rendering
            // For now, we'll keep the existing HTML structure but mark it for extraction
            return `
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
                        this.displayOffers(data.offers);
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
                        this.displayOffers(data.offers);
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
            const chatArea = document.querySelector('.p-5.py-12');
            if (!chatArea) return;
            
            // Clear previous offers data
            this.offersData.clear();

            // Use the OfferDisplay module if available
            if (window.OfferDisplay) {
                window.OfferDisplay.displayOffers(offers, chatArea);
            } else {
                // Fallback to basic display
                this.displayBasicOffers(offers, chatArea);
            }
        }

        /**
         * Basic offers display fallback
         */
        displayBasicOffers(offers, chatArea) {
            const offersHTML = `
                <div class="bg-white dark:bg-gray-800 shadow-2xl rounded-3xl rounded-bl-lg p-8 max-w-6xl border border-gray-100 dark:border-gray-700 backdrop-blur-sm relative overflow-hidden">
                    <div class="text-center mb-6">
                        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Vos Offres Parfaites</h2>
                        <p class="text-base text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                            Voici les 3 meilleures offres sélectionnées spécialement pour vous selon vos préférences
                        </p>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        ${offers.map((offer, index) => this.createBasicOfferCard(offer, index)).join('')}
                    </div>
                </div>
            `;
            
            chatArea.insertAdjacentHTML('beforeend', offersHTML);
            this.refreshLucideIcons();
        }

        /**
         * Create a basic offer card
         */
        createBasicOfferCard(offer, index) {
            return `
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div class="p-6">
                        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">
                            ${offer.product_name || 'Offre de voyage'}
                        </h3>
                        <p class="text-gray-600 dark:text-gray-300 mb-4">
                            ${offer.description || 'Description non disponible'}
                        </p>
                        <a href="${offer.price_url || '#'}" target="_blank" 
                           class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors duration-200">
                            Voir l'offre
                        </a>
                    </div>
                </div>
            `;
        }

        /**
         * Show offer details modal
         */
        showOfferDetails(offerReference) {
            console.log('🔍 Opening modal for offer:', offerReference);
            
            // Remove any existing modals first
            const existingModals = document.querySelectorAll('.offer-details-modal');
            existingModals.forEach(modal => modal.remove());
            
            // Get offer data from the Map
            const offerData = this.offersData.get(offerReference);
            
            if (!offerData) {
                console.error('❌ No offer data found for reference:', offerReference);
                return;
            }
            
            // Use Twig template for modal rendering
            const modalHtml = this.renderOfferDetailsModal(offerData, offerReference);
            
            const modal = document.createElement('div');
            modal.className = 'offer-details-modal fixed inset-0 bg-black/95 flex items-center justify-center z-50 backdrop-blur-md';
            modal.innerHTML = modalHtml;
            
            document.body.appendChild(modal);
            this.refreshLucideIcons();
            
            // Add click outside to close
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
        }

        /**
         * Render offer details modal template
         */
        renderOfferDetailsModal(offerData, offerReference) {
            // This would be replaced with actual Twig template rendering
            // For now, return a simplified modal structure
            return `
                <div class="w-full h-full flex flex-col lg:flex-row bg-white dark:bg-gray-900 relative overflow-hidden">
                    <button onclick="this.closest('.offer-details-modal').remove()" class="absolute top-6 right-6 z-50 bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white rounded-full p-4 transition-all duration-300">
                        <i data-lucide="x" class="w-6 h-6"></i>
                    </button>
                    <div class="w-full lg:w-1/2 h-1/2 lg:h-full overflow-y-auto bg-white dark:bg-gray-900 p-6">
                        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">${offerData?.product_name || 'Offre de voyage'}</h1>
                        <p class="text-gray-600 dark:text-gray-400 mb-6">${offerData?.description || 'Description non disponible'}</p>
                        <a href="${offerData?.price_url || '#'}" target="_blank" 
                           class="bg-red-600 hover:bg-red-700 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-300">
                            Réserver maintenant
                        </a>
                    </div>
                </div>
            `;
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
            overlay.id = 'confirmation-loading-overlay';
            overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            overlay.innerHTML = `
                <div class="bg-white dark:bg-gray-800 rounded-lg p-6 flex items-center space-x-3">
                    <div class="loader"></div>
                    <span class="text-gray-700 dark:text-gray-300">Traitement en cours...</span>
                </div>
            `;
            document.body.appendChild(overlay);
        }

        hideLoadingState() {
            const overlay = document.getElementById('confirmation-loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        }

        removeConfirmationUI() {
            const confirmationElements = document.querySelectorAll('.flex.justify-start.mb-6.animate-fade-in');
            confirmationElements.forEach(element => {
                if (element.querySelector('button[onclick*="confirmPreferences"]')) {
                    element.remove();
                }
            });
        }

        addConfirmationMessage(message) {
            const chatArea = document.querySelector('.p-5.py-12');
            if (!chatArea) return;

            const messageDiv = document.createElement('div');
            messageDiv.className = 'flex justify-start mb-6';
            messageDiv.innerHTML = `
                <div class="bg-white dark:bg-gray-800 shadow-2xl rounded-3xl rounded-bl-lg p-6 max-w-3xl border border-gray-200 dark:border-gray-700">
                    <p class="text-gray-700 dark:text-gray-300">${message}</p>
                </div>
            `;
            
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        showError(message) {
            const chatArea = document.querySelector('.p-5.py-12');
            if (!chatArea) return;

            const errorDiv = document.createElement('div');
            errorDiv.className = 'flex justify-start mb-6';
            errorDiv.innerHTML = `
                <div class="bg-red-100 dark:bg-red-900/30 border border-red-200 dark:border-red-700 shadow-2xl rounded-3xl rounded-bl-lg p-6 max-w-3xl">
                    <p class="text-red-700 dark:text-red-300">${message}</p>
                </div>
            `;
            
            chatArea.appendChild(errorDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        init() {
            // Initialize the confirmation flow
            console.log('🎯 ConfirmationFlow initialized');
        }
    }

    // Make available globally
    window.confirmationFlow = new ConfirmationFlow();
} 