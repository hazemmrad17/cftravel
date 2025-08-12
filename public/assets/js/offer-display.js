/**
 * Travel Offer Display Module
 * Handles rendering of AI-recommended travel offers and detailed program views
 */

const OfferDisplay = {
    // Render a collection of offer cards
    renderOfferCards: function(offers, containerId = 'ai-offers-container') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container with ID ${containerId} not found`);
            return;
        }

        // Clear previous offers
        container.innerHTML = '';
        
        // Create grid container
        const gridContainer = document.createElement('div');
        gridContainer.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4 mb-6';
        
        // Add offers to the grid
        offers.forEach((offer, index) => {
            const offerCard = this.createOfferCard(offer, index);
            gridContainer.appendChild(offerCard);
        });
        
        container.appendChild(gridContainer);
    },
    

    
    // Generate dynamic gradient colors based on destination
    getGradientColors: function(country, fallbackIndex) {
        // Predefined gradients for popular destinations
        const countryGradients = {
            'Japon': 'from-pink-500 to-red-600',      // Cherry blossom colors
            'France': 'from-blue-500 to-red-600',     // French flag colors
            'Italie': 'from-green-500 to-red-600',    // Italian flag colors
            'Espagne': 'from-yellow-500 to-red-600',  // Spanish flag colors
            'Grèce': 'from-blue-500 to-cyan-600',     // Mediterranean colors
            'Thaïlande': 'from-green-500 to-yellow-600', // Tropical colors
            'Maldives': 'from-blue-400 to-cyan-600',  // Ocean colors
            'Égypte': 'from-yellow-500 to-amber-700', // Desert colors
            'Maroc': 'from-red-500 to-orange-600',    // Moroccan colors
            'États-Unis': 'from-blue-600 to-red-600', // American flag colors
            'Chine': 'from-red-600 to-yellow-500',    // Chinese flag colors
            'Inde': 'from-orange-500 to-green-600',   // Indian flag colors
            'Brésil': 'from-green-500 to-yellow-500', // Brazilian flag colors
            'Australie': 'from-blue-500 to-yellow-600', // Australian colors
            'Canada': 'from-red-600 to-white',        // Canadian flag colors
            'Mexique': 'from-green-600 to-red-600',   // Mexican flag colors
            'Afrique du Sud': 'from-green-600 to-yellow-500' // South African colors
        };
        
        // Fallback gradients if country not found
        const fallbackGradients = [
            'from-blue-500 to-purple-600',
            'from-green-500 to-blue-600', 
            'from-orange-500 to-red-600',
            'from-purple-500 to-pink-600',
            'from-teal-500 to-green-600'
        ];
        
        // Return country-specific gradient or fallback
        return countryGradients[country] || fallbackGradients[fallbackIndex % fallbackGradients.length];
    },
    
    // Create a single offer card element
    createOfferCard: function(offer, index) {
        // Format destinations
        const destinations = offer.destinations.map(d => `${d.city} (${d.country})`).join(', ');
        
        // Generate gradient based on destination
        const gradient = this.getGradientColors(offer.destinations[0]?.country || '', index);
        
        // Get the best image from the database
        const mainImage = offer.images && offer.images.length > 0 ? offer.images[0] : '/assets/images/placeholder-travel.svg';
        
        // Get reservation URL (use first one if multiple, fallback to price_url)
        const reservationUrl = offer.reservation_urls && offer.reservation_urls.length > 0 
            ? offer.reservation_urls[0] 
            : offer.price_url || '#';
        
        // Get highlights from database
        const highlights = offer.highlights && offer.highlights.length > 0 
            ? offer.highlights.slice(0, 2).map(h => h.text || h.title || h)
            : [];
        
        // Create card container
        const card = document.createElement('div');
        card.className = 'group bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-200 dark:border-gray-700 transform hover:-translate-y-1 hover:scale-105';
        
        // Set inner HTML with all card content
        card.innerHTML = `
            <div class="relative">
                <div class="absolute inset-0 bg-gradient-to-br ${gradient} opacity-20 group-hover:opacity-30 transition-opacity duration-300"></div>
                <img src="${mainImage}" alt="${offer.product_name}" class="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-300" onerror="this.src='/assets/images/placeholder-travel.svg'">
                
                <!-- Duration badge -->
                <div class="absolute top-3 right-3">
                    <span class="bg-white/90 backdrop-blur-sm text-gray-900 text-xs px-3 py-1 rounded-full font-semibold shadow-lg">
                        ${offer.duration} jours
                    </span>
                </div>
                
                <!-- Match score -->
                <div class="absolute bottom-3 left-3">
                    <div class="flex items-center bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full">
                        <div class="flex text-yellow-400">
                            ${this.generateStars(offer.match_score || 0.8)}
                        </div>
                        <span class="text-xs text-gray-700 dark:text-gray-300 ml-1 font-medium">${Math.round((offer.match_score || 0.8) * 5 * 10) / 10}</span>
                    </div>
                </div>
                
                <!-- ASIA Badge -->
                <div class="absolute top-3 left-3">
                    <div class="bg-gradient-to-r from-red-500 to-red-600 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg">
                        ASIA
                    </div>
                </div>
                
                <!-- Match score badge -->
                <div class="absolute bottom-3 right-3">
                    <div class="bg-gradient-to-r from-emerald-500 to-green-600 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg">
                        ${Math.round((offer.match_score || 0.8) * 100)}%
                    </div>
                </div>
            </div>
            
            <div class="p-6">
                <!-- Title -->
                <h3 class="font-bold text-lg text-gray-900 dark:text-white mb-3 line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-200">
                    ${offer.product_name}
                </h3>
                
                <!-- Destinations -->
                <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 mb-3">
                    <svg class="w-4 h-4 mr-2 text-red-500 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <span class="line-clamp-1">${destinations}</span>
                </div>
                
                <!-- Departure -->
                <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 mb-4">
                    <svg class="w-4 h-4 mr-2 text-red-500 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    <span>Départ: ${offer.departure_city}</span>
                </div>
                
                <!-- Highlights from database -->
                <div class="mb-4">
                    <div class="flex flex-wrap gap-1">
                        ${highlights.map(highlight => `
                            <span class="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs px-2 py-1 rounded-full">
                                ${highlight}
                            </span>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Features from database -->
                <div class="mb-4">
                    <div class="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        ${offer.offer_type || 'Circuit organisé'}
                    </div>
                </div>
                
                <!-- Price and Action -->
                <div class="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                        <span class="font-semibold text-green-600">€€€</span>
                        <span class="ml-1">${offer.min_group_size ? `Groupe ${offer.min_group_size}-${offer.max_group_size || '18'}` : 'Petit groupe'}</span>
                    </div>
                    <div class="flex gap-2">
                        ${reservationUrl ? `
                            <a href="${reservationUrl}" target="_blank" class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white text-sm px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg">
                                Réserver
                            </a>
                        ` : ''}
                        <button onclick="OfferDisplay.showOfferDetails('${offer.reference}')" class="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white text-sm px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg">
                            Détails
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    },
    
    // Generate star rating based on match score
    generateStars: function(score) {
        const fullStars = Math.floor(score * 5);
        const halfStar = score * 5 - fullStars >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        let stars = '';
        for (let i = 0; i < fullStars; i++) stars += '★';
        if (halfStar) stars += '★';
        for (let i = 0; i < emptyStars; i++) stars += '☆';
        
        return stars;
    },
    
    // Show detailed program for an offer
    showOfferDetails: function(offerReference) {
        // Send a message to request detailed program
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('chat-send-btn');
        
        if (chatInput && sendButton) {
            chatInput.value = `Montre-moi les détails du programme ${offerReference}`;
            sendButton.click();
        }
    },
    
    // Render detailed program view
    renderDetailedProgram: function(program, containerId = 'detailed-program-container') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container with ID ${containerId} not found`);
            return;
        }
        
        // Clear previous content
        container.innerHTML = '';
        
        // Get the best image from database
        const mainImage = program.images && program.images.length > 0 ? program.images[0] : '/assets/images/placeholder-travel.svg';
        
        // Get reservation URL from database
        const reservationUrl = program.reservation_urls && program.reservation_urls.length > 0 
            ? program.reservation_urls[0] 
            : program.price_url || '#';
        
        // Format destinations
        const destinations = program.destinations && program.destinations.length > 0 
            ? program.destinations.map(d => `${d.city} (${d.country})`).join(', ')
            : '';
        
        // Create detailed view
        const detailView = document.createElement('div');
        detailView.className = 'bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6';
        
        // Header section with image
        detailView.innerHTML = `
            <div class="relative">
                <img src="${mainImage}" alt="${program.product_name}" class="w-full h-64 object-cover" onerror="this.src='/assets/images/placeholder-travel.svg'">
                <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
                <div class="absolute bottom-0 left-0 p-6 text-white">
                    <h2 class="text-2xl font-bold mb-2">${program.product_name}</h2>
                    <p class="text-sm opacity-90">${program.description || ''}</p>
                </div>
            </div>
            
            <div class="p-6">
                <!-- Overview -->
                <div class="mb-6">
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Aperçu</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="bg-gray-50 dark:bg-gray-700/30 p-4 rounded-lg">
                            <div class="flex items-center mb-2">
                                <svg class="w-5 h-5 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                                <h4 class="font-semibold text-gray-900 dark:text-white">Durée</h4>
                            </div>
                            <p class="text-gray-600 dark:text-gray-300">${program.duration || 0} jours</p>
                        </div>
                        <div class="bg-gray-50 dark:bg-gray-700/30 p-4 rounded-lg">
                            <div class="flex items-center mb-2">
                                <svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                </svg>
                                <h4 class="font-semibold text-gray-900 dark:text-white">Destinations</h4>
                            </div>
                            <p class="text-gray-600 dark:text-gray-300">${destinations}</p>
                        </div>
                        <div class="bg-gray-50 dark:bg-gray-700/30 p-4 rounded-lg">
                            <div class="flex items-center mb-2">
                                <svg class="w-5 h-5 text-purple-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                                </svg>
                                <h4 class="font-semibold text-gray-900 dark:text-white">Type</h4>
                            </div>
                            <p class="text-gray-600 dark:text-gray-300">${program.offer_type || 'Circuit organisé'}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Highlights from database -->
                <div class="mb-6">
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Points forts</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        ${program.highlights && program.highlights.length > 0 ? program.highlights.map(highlight => `
                            <div class="flex items-start">
                                <svg class="w-5 h-5 text-amber-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
                                </svg>
                                <p class="text-gray-700 dark:text-gray-300">${highlight.text || highlight.title || highlight}</p>
                            </div>
                        `).join('') : '<p class="text-gray-500 dark:text-gray-400">Aucun point fort spécifié</p>'}
                    </div>
                </div>
                
                <!-- Programme from database -->
                <div class="mb-6">
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Programme</h3>
                    <div class="bg-gray-50 dark:bg-gray-700/30 p-4 rounded-lg">
                        <p class="text-gray-700 dark:text-gray-300 whitespace-pre-line">${program.programme || 'Programme détaillé non disponible'}</p>
                    </div>
                </div>
                
                <!-- Dates from database -->
                <div class="mb-6">
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Dates de départ</h3>
                    <div class="flex flex-wrap gap-2">
                        ${program.dates && program.dates.length > 0 ? program.dates.map(date => `
                            <span class="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-3 py-1 rounded-full text-sm">
                                ${date}
                            </span>
                        `).join('') : '<p class="text-gray-500 dark:text-gray-400">Dates non disponibles</p>'}
                    </div>
                </div>
                
                <!-- Group size from database -->
                <div class="mb-6">
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Informations pratiques</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-gray-50 dark:bg-gray-700/30 p-4 rounded-lg">
                            <h4 class="font-semibold text-gray-900 dark:text-white mb-2">Taille du groupe</h4>
                            <p class="text-gray-600 dark:text-gray-300">
                                ${program.min_group_size ? `${program.min_group_size} - ${program.max_group_size || '18'} participants` : 'Groupe non spécifié'}
                            </p>
                        </div>
                        <div class="bg-gray-50 dark:bg-gray-700/30 p-4 rounded-lg">
                            <h4 class="font-semibold text-gray-900 dark:text-white mb-2">Ville de départ</h4>
                            <p class="text-gray-600 dark:text-gray-300">${program.departure_city || 'Non spécifié'}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Call to Action with database URLs -->
                <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 p-6 rounded-xl border border-blue-100 dark:border-blue-800/30 text-center">
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Intéressé par ce voyage?</h3>
                    <p class="text-gray-600 dark:text-gray-400 mb-4">Contactez-nous pour plus d'informations ou pour réserver</p>
                    <div class="flex gap-3 justify-center">
                        ${reservationUrl ? `
                            <a href="${reservationUrl}" target="_blank" class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg font-medium">
                                Réserver maintenant
                            </a>
                        ` : ''}
                        <button onclick="OfferDisplay.closeDetails()" class="bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg font-medium">
                            Fermer
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(detailView);
    },
    
    // Close details view
    closeDetails: function() {
        const container = document.getElementById('detailed-program-container');
        if (container) {
            container.innerHTML = '';
        }
    }
};