/**
 * Offer Display Module for ASIA.fr Agent Frontend
 */

// Only create if not already defined
if (typeof OfferDisplay === 'undefined') {
    let OfferDisplay = {
        currentOffers: [],
        maxOffers: 3,

        displayOffers: function(offers, chatArea) {
            if (!offers || !Array.isArray(offers) || offers.length === 0) {
                console.warn('No offers to display');
                return;
            }

            this.currentOffers = offers.slice(0, this.maxOffers);
            
            // Create offers container
            const offersContainer = document.createElement('div');
            offersContainer.className = 'offers-container mb-6';
            offersContainer.innerHTML = this.renderOffersTemplate(this.currentOffers);
            
            // Insert before the last message
            const lastMessage = chatArea.lastElementChild;
            if (lastMessage) {
                chatArea.insertBefore(offersContainer, lastMessage);
            } else {
                chatArea.appendChild(offersContainer);
            }
            
            // Scroll to offers
            setTimeout(() => {
                offersContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
            
            console.log(`🎁 Displayed ${this.currentOffers.length} offers`);
        },

        renderOffersTemplate: function(offers) {
            let offersHtml = '<div class="offers-grid space-y-4">';
            
            offers.forEach((offer, index) => {
                offersHtml += this.renderOfferCard(offer, index);
            });
            
            offersHtml += '</div>';
            return offersHtml;
        },

        renderOfferCard: function(offer, index) {
            const highlightsHtml = this.renderHighlights(offer.highlights);
            
            return `
                <div class="offer-card bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-shadow duration-300">
                    <div class="p-6">
                        <div class="flex items-start justify-between mb-4">
                            <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                                ${offer.product_name || 'Offre de voyage'}
                            </h3>
                            <span class="px-3 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-sm font-medium rounded-full">
                                Offre ${index + 1}
                            </span>
                        </div>
                        
                        ${highlightsHtml}
                        
                        <p class="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                            ${offer.description || 'Description non disponible'}
                        </p>
                        
                        <div class="flex items-center justify-between">
                            <div class="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                                ${this.renderOfferDetails(offer)}
                            </div>
                            
                            <a href="${offer.price_url || '#'}" 
                               target="_blank" 
                               class="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors duration-200">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                </svg>
                                Voir l'offre
                            </a>
                        </div>
                    </div>
                </div>
            `;
        },

        renderHighlights: function(highlights) {
            if (!highlights || !Array.isArray(highlights) || highlights.length === 0) {
                return '';
            }

            let highlightsHtml = '<div class="mb-4"><h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Points forts :</h4><ul class="space-y-1">';
            
            highlights.forEach(highlight => {
                highlightsHtml += `
                    <li class="flex items-start text-sm text-gray-600 dark:text-gray-400">
                        <svg class="w-4 h-4 mr-2 mt-0.5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        <span><strong>${highlight.title || ''}:</strong> ${highlight.text || ''}</span>
                    </li>
                `;
            });
            
            highlightsHtml += '</ul></div>';
            return highlightsHtml;
        },

        renderOfferDetails: function(offer) {
            const details = [];
            
            if (offer.duration) {
                details.push(`
                    <div class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        ${offer.duration}
                    </div>
                `);
            }
            
            if (offer.destinations && Array.isArray(offer.destinations)) {
                details.push(`
                    <div class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        </svg>
                        ${offer.destinations.length} destination${offer.destinations.length > 1 ? 's' : ''}
                    </div>
                `);
            }
            
            if (offer.offer_type) {
                details.push(`
                    <div class="flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                        </svg>
                        ${offer.offer_type}
                    </div>
                `);
            }
            
            return details.join('');
        },

        clearOffers: function(chatArea) {
            const offersContainer = chatArea.querySelector('.offers-container');
            if (offersContainer) {
                offersContainer.remove();
            }
            this.currentOffers = [];
        },

        getCurrentOffers: function() {
            return this.currentOffers;
        },

        updateOffers: function(newOffers, chatArea) {
            this.clearOffers(chatArea);
            this.displayOffers(newOffers, chatArea);
        }
    };

    // Make available globally
    window.OfferDisplay = OfferDisplay;
} 