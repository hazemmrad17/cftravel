/**
 * Confirmation Flow Handler for ASIA.fr Agent
 * Handles the confirmation flow when users provide sufficient travel details
 */

class ConfirmationFlow {
    constructor() {
        this.API_BASE_URL = 'http://localhost:8001';
        this.currentState = null;
        this.preferences = {};
    }

    /**
     * Display confirmation request with user preferences
     */
    displayConfirmationRequest(preferences, confirmationSummary) {
        const chatArea = document.querySelector('.p-5.py-12');
        if (!chatArea) return;

        const confirmationDiv = document.createElement('div');
        confirmationDiv.className = 'flex justify-start mb-6';
                 confirmationDiv.innerHTML = `
             <div class="bg-chat-ai bg-white dark:bg-gray-800 shadow-theme-xs rounded-3xl rounded-bl-lg p-6 max-w-4xl border border-gray-200 dark:border-gray-700">
                <div class="mb-6">
                                         <div class="flex items-center mb-4">
                         <div class="w-10 h-10 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-4">
                             <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                             </svg>
                         </div>
                         <div>
                             <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Parfait ! Confirmons vos préférences</h3>
                             <p class="text-gray-600 dark:text-gray-300">J'ai rassemblé tous les détails nécessaires pour trouver vos offres de voyage parfaites</p>
                         </div>
                     </div>
                </div>

                <!-- Preferences Summary -->
                <div class="mb-6">
                                         <h4 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                         <svg class="w-5 h-5 mr-2 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                         </svg>
                         Your Travel Preferences
                     </h4>
                                         <div class="bg-gradient-to-r from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-xl p-4 border border-red-200 dark:border-red-700">
                         <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                             ${this.renderPreferenceItems(preferences)}
                         </div>
                     </div>
                </div>

                <!-- Confirmation Message -->
                <div class="mb-6">
                                         <div class="bg-gradient-to-r from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-xl p-4 border border-red-200 dark:border-red-700">
                         <div class="flex items-start">
                             <div class="w-8 h-8 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                                 <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                 </svg>
                             </div>
                             <div>
                                 <p class="text-red-800 dark:text-red-200 font-medium mb-2">Prêt à découvrir vos offres parfaites !</p>
                                 <p class="text-red-700 dark:text-red-300 text-sm">
                                     Basé sur vos préférences, je vais vous montrer les 3 meilleures offres de voyage qui correspondent exactement à ce que vous recherchez. 
                                     Chaque offre sera soigneusement sélectionnée et classée par notre IA pour garantir la correspondance parfaite.
                                 </p>
                             </div>
                         </div>
                     </div>
                </div>

                <!-- Action Buttons -->
                <div class="flex flex-col sm:flex-row gap-4">
                                         <button onclick="confirmationFlow.confirmPreferences()" 
                             class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white dark:text-white px-8 py-3 rounded-xl font-bold transition-all duration-300 transform hover:scale-105 shadow-lg flex items-center justify-center">
                         <svg class="w-5 h-5 mr-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                         </svg>
                         Yes, show me the offers!
                     </button>
                     <button onclick="confirmationFlow.modifyPreferences()" 
                             class="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white dark:text-white px-8 py-3 rounded-xl font-bold transition-all duration-300 transform hover:scale-105 shadow-lg flex items-center justify-center">
                         <svg class="w-5 h-5 mr-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                         </svg>
                         I want to modify something
                     </button>
                </div>
            </div>
        `;

        chatArea.appendChild(confirmationDiv);
        chatArea.scrollTop = chatArea.scrollHeight;

        // Store current preferences
        this.preferences = preferences;
    }

    /**
     * Render preference items in a grid
     */
    renderPreferenceItems(preferences) {
        const items = [];
        
        if (preferences.destination) {
            items.push(`
                                 <div class="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                     <div class="w-8 h-8 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-3">
                         <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                         </svg>
                     </div>
                     <div>
                         <p class="text-sm font-medium text-gray-900 dark:text-white">Destination</p>
                         <p class="text-xs text-gray-600 dark:text-gray-300">${preferences.destination}</p>
                     </div>
                 </div>
            `);
        }

        if (preferences.duration) {
            items.push(`
                                 <div class="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                     <div class="w-8 h-8 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-3">
                         <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                         </svg>
                     </div>
                     <div>
                         <p class="text-sm font-medium text-gray-900 dark:text-white">Duration</p>
                         <p class="text-xs text-gray-600 dark:text-gray-300">${preferences.duration} jours</p>
                     </div>
                 </div>
            `);
        }

        if (preferences.style) {
            items.push(`
                                 <div class="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                     <div class="w-8 h-8 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-3">
                         <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                         </svg>
                     </div>
                     <div>
                         <p class="text-sm font-medium text-gray-900 dark:text-white">Travel Style</p>
                         <p class="text-xs text-gray-600 dark:text-gray-300">${preferences.style}</p>
                     </div>
                 </div>
            `);
        }

        if (preferences.budget) {
            items.push(`
                                 <div class="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                     <div class="w-8 h-8 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-3">
                         <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                         </svg>
                     </div>
                     <div>
                         <p class="text-sm font-medium text-gray-900 dark:text-white">Budget</p>
                         <p class="text-xs text-gray-600 dark:text-gray-300">${preferences.budget}</p>
                     </div>
                 </div>
            `);
        }

        if (preferences.travelers) {
            items.push(`
                                 <div class="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                     <div class="w-8 h-8 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-3">
                         <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                         </svg>
                     </div>
                     <div>
                         <p class="text-sm font-medium text-gray-900 dark:text-white">Travelers</p>
                         <p class="text-xs text-gray-600 dark:text-gray-300">${preferences.travelers} personnes</p>
                     </div>
                 </div>
            `);
        }

        if (preferences.timing) {
            items.push(`
                                 <div class="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                     <div class="w-8 h-8 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-3">
                         <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                         </svg>
                     </div>
                     <div>
                         <p class="text-sm font-medium text-gray-900 dark:text-white">Timing</p>
                         <p class="text-xs text-gray-600 dark:text-gray-300">${preferences.timing}</p>
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
                // Remove confirmation UI
                this.removeConfirmationUI();

                // Add modification message
                this.addConfirmationMessage(data.message);
            } else {
                this.showError('Failed to modify preferences. Please try again.');
            }
        } catch (error) {
            console.error('Error modifying preferences:', error);
            this.showError('Network error. Please check your connection and try again.');
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

        const offersContainer = document.createElement('div');
        offersContainer.className = 'flex justify-start mb-6';
        offersContainer.innerHTML = `
            <div class="bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg p-6 max-w-6xl">
                                 <div class="mb-6">
                     <div class="flex items-center mb-3">
                         <div class="w-8 h-8 bg-gradient-to-r from-red-600 to-red-700 rounded-full flex items-center justify-center mr-3">
                             <span class="text-white text-sm font-bold">ASIA</span>
                         </div>
                         <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Your Perfect Travel Offers</h3>
                     </div>
                     <p class="text-sm text-gray-600 dark:text-gray-300">Voici les 3 meilleures offres qui correspondent parfaitement à vos préférences</p>
                 </div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${offers.map((offer, index) => this.createOfferCard(offer, index)).join('')}
                </div>
            </div>
        `;
        chatArea.appendChild(offersContainer);
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    /**
     * Create a beautiful offer card
     */
    createOfferCard(offer, index) {
        const destinations = offer.destinations.map(d => `${d.city} (${d.country})`).join(', ');
        const highlights = offer.highlights.map(h => h.text).join(', ');
        const imageUrl = offer.images && offer.images.length > 0 ? offer.images[0] : '/assets/images/placeholder-travel.svg';
        
        // Generate a beautiful gradient based on index
        const gradients = [
            'from-blue-500 to-purple-600',
            'from-green-500 to-blue-600', 
            'from-orange-500 to-red-600',
            'from-purple-500 to-pink-600',
            'from-teal-500 to-green-600'
        ];
        const gradient = gradients[index % gradients.length];
        
        return `
            <div class="group bg-white dark:bg-gray-800 rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 dark:border-gray-700 transform hover:-translate-y-2 hover:scale-105 flex flex-col h-full" 
                 data-offer-reference="${offer.reference}" 
                 data-offer-data='${JSON.stringify(offer)}'>
                <div class="relative">
                    <div class="absolute inset-0 bg-gradient-to-br ${gradient} opacity-10 group-hover:opacity-20 transition-opacity duration-500"></div>
                    <img src="${imageUrl}" alt="${offer.product_name}" class="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-700" onerror="this.src='/assets/images/placeholder-travel.svg'">
                    
                    <!-- Duration badge -->
                    <div class="absolute top-4 right-4">
                        <span class="bg-white/95 backdrop-blur-sm text-gray-900 text-sm px-4 py-2 rounded-full font-bold shadow-xl">
                            ${offer.duration} jours
                        </span>
                    </div>
                    
                    <!-- Rating -->
                    <div class="absolute bottom-4 left-4">
                        <div class="flex items-center bg-white/95 backdrop-blur-sm px-3 py-2 rounded-full shadow-xl">
                            <div class="flex text-yellow-400 text-sm">
                                ${'★'.repeat(4)}${'☆'.repeat(1)}
                            </div>
                                                         <span class="text-sm text-gray-700 dark:text-gray-300 ml-2 font-bold">4.8</span>
                        </div>
                    </div>
                    
                                         <!-- ASIA.fr Badge -->
                     <div class="absolute top-4 left-4">
                         <div class="bg-gradient-to-r from-red-600 to-red-700 text-white text-xs px-3 py-1 rounded-full font-bold shadow-xl">
                             ASIA.fr
                         </div>
                     </div>
                </div>
                
                <div class="p-6 flex-1 flex flex-col">
                    <!-- Title -->
                    <h3 class="font-bold text-xl text-gray-900 dark:text-white mb-4 line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">
                        ${offer.product_name}
                    </h3>
                    
                                         <!-- Destinations -->
                     <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 mb-4">
                         <svg class="w-5 h-5 mr-3 text-red-500 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                         </svg>
                         <span class="line-clamp-1 font-medium">${destinations}</span>
                     </div>
                     
                     <!-- Departure -->
                     <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 mb-4">
                         <svg class="w-5 h-5 mr-3 text-red-500 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                         </svg>
                         <span class="font-medium">Départ: ${offer.departure_city}</span>
                     </div>
                    
                    <!-- Description -->
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-5 line-clamp-3 leading-relaxed">
                        ${offer.description}
                    </p>
                    
                    <!-- Match Score (simplified) -->
                    ${offer.match_score ? `
                        <div class="mb-4 flex items-center justify-between">
                            <span class="text-sm text-gray-600 dark:text-gray-300">Match:</span>
                            <span class="text-sm font-bold text-blue-600 dark:text-blue-400">${Math.round(offer.match_score * 100)}%</span>
                        </div>
                    ` : ''}
                    
                    <!-- Action Buttons -->
                    <div class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700 mt-auto">
                        <div class="text-sm text-gray-500 dark:text-gray-400">
                            <span class="font-bold text-green-600 text-lg">€€€</span>
                            <span class="ml-2">Petit groupe • Premium</span>
                        </div>
                        <div class="flex gap-2">
                            ${offer.price_url ? `
                                <a href="${offer.price_url}" target="_blank" class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white text-xs px-3 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg font-medium">
                                    Réserver
                                </a>
                            ` : ''}
                            <button onclick="confirmationFlow.showOfferDetails('${offer.reference}')" class="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white text-xs px-3 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg font-medium">
                                Détails
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Show offer details modal
     */
    showOfferDetails(offerReference) {
        // Find the offer data from the current offers
        const offerCards = document.querySelectorAll('[data-offer-reference]');
        let offerData = null;
        
        offerCards.forEach(card => {
            if (card.getAttribute('data-offer-reference') === offerReference) {
                offerData = JSON.parse(card.getAttribute('data-offer-data') || '{}');
            }
        });
        
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-bold text-gray-900 dark:text-white">Détails de l'offre</h2>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <div class="space-y-4">
                    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <h3 class="font-bold text-lg text-gray-900 dark:text-white mb-2">${offerData?.product_name || 'Offre de voyage'}</h3>
                        <p class="text-gray-600 dark:text-gray-300 mb-2">Référence: ${offerReference}</p>
                        ${offerData?.description ? `<p class="text-gray-600 dark:text-gray-300">${offerData.description}</p>` : ''}
                    </div>
                    
                    ${offerData?.highlights && offerData.highlights.length > 0 ? `
                        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                            <h4 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">Points forts</h4>
                            <ul class="space-y-1">
                                ${offerData.highlights.slice(0, 5).map(highlight => `
                                    <li class="text-sm text-blue-800 dark:text-blue-200 flex items-center">
                                        <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                        </svg>
                                        ${highlight.text}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${offerData?.ai_reasoning ? `
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                            <h4 class="font-semibold text-green-900 dark:text-green-100 mb-2">Pourquoi cette offre vous convient</h4>
                            <p class="text-sm text-green-800 dark:text-green-200">${offerData.ai_reasoning}</p>
                        </div>
                    ` : ''}
                </div>
                <div class="mt-6 flex justify-end space-x-3">
                    <button onclick="this.closest('.fixed').remove()" class="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100">
                        Fermer
                    </button>
                    ${offerData?.price_url ? `
                        <a href="${offerData.price_url}" target="_blank" class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-6 py-2 rounded-lg transition-all duration-200 font-medium">
                            Réserver maintenant
                        </a>
                    ` : `
                        <button onclick="confirmationFlow.bookOffer('${offerReference}')" class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-4 py-2 rounded-lg transition-all duration-200">
                            Réserver
                        </button>
                    `}
                </div>
            </div>
        `;
        document.body.appendChild(modal);
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
        const chatArea = document.querySelector('.p-5.py-12');
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
        const chatArea = document.querySelector('.p-5.py-12');
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
}

// Initialize the confirmation flow
const confirmationFlow = new ConfirmationFlow();

// Make it available globally
window.confirmationFlow = confirmationFlow; 