/**
 * Error Message Component
 * Displays styled error messages with different colors based on error type and severity
 */

class ErrorMessage {
    constructor() {
        this.errorColors = {
            // Error severity colors
            low: '#ff9800',      // Orange
            medium: '#f44336',   // Red
            high: '#d32f2f',     // Dark red
            critical: '#b71c1c', // Very dark red
            
            // Error type specific colors
            api_key_invalid: '#e91e63',      // Pink
            api_tokens_depleted: '#ff5722',  // Deep orange
            stream_error: '#2196f3',         // Blue
            message_send_error: '#ff9800',   // Orange
            message_receive_error: '#ff9800', // Orange
            network_error: '#9c27b0',        // Purple
            server_error: '#d32f2f',         // Dark red
            validation_error: '#ff9800',     // Orange
            memory_error: '#607d8b',         // Blue grey
            processing_error: '#795548',     // Brown
            unknown_error: '#757575'         // Grey
        };
    }

    /**
     * Create and display an error message bubble
     * @param {Object} errorData - Error data from API
     * @param {string} errorData.error_type - Type of error
     * @param {string} errorData.severity - Error severity
     * @param {string} errorData.user_message - User-friendly message
     * @param {string} errorData.technical_details - Technical details (optional)
     * @param {string} containerId - ID of container to append error to
     */
    displayError(errorData, containerId = 'chat-messages') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Error container not found:', containerId);
            return;
        }

        // Create error message element
        const errorElement = this.createErrorElement(errorData);
        
        // Add to container
        container.appendChild(errorElement);
        
        // Scroll to error
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
        
        // Auto-remove after 10 seconds for non-critical errors
        if (errorData.severity !== 'critical') {
            setTimeout(() => {
                this.fadeOutAndRemove(errorElement);
            }, 10000);
        }
    }

    /**
     * Create error message HTML element
     */
    createErrorElement(errorData) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message-bubble';
        errorDiv.setAttribute('data-error-type', errorData.error_type);
        errorDiv.setAttribute('data-error-severity', errorData.severity);
        
        // Get color based on error type and severity
        const color = this.getErrorColor(errorData.error_type, errorData.severity);
        
        // Create error icon based on type
        const icon = this.getErrorIcon(errorData.error_type);
        
        // Create HTML content
        errorDiv.innerHTML = `
            <div class="error-content" style="border-left: 4px solid ${color};">
                <div class="error-header">
                    <span class="error-icon">${icon}</span>
                    <span class="error-title">${this.getErrorTitle(errorData.error_type)}</span>
                    <button class="error-close" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="error-message">${errorData.user_message}</div>
                ${errorData.technical_details ? `
                    <div class="error-details">
                        <details>
                            <summary>Détails techniques</summary>
                            <pre>${errorData.technical_details}</pre>
                        </details>
                    </div>
                ` : ''}
            </div>
        `;
        
        return errorDiv;
    }

    /**
     * Get error color based on type and severity
     */
    getErrorColor(errorType, severity) {
        // Try error type specific color first
        if (this.errorColors[errorType]) {
            return this.errorColors[errorType];
        }
        
        // Fall back to severity color
        return this.errorColors[severity] || this.errorColors.medium;
    }

    /**
     * Get error icon based on type
     */
    getErrorIcon(errorType) {
        const icons = {
            api_key_invalid: '🔑',
            api_tokens_depleted: '💳',
            stream_error: '📡',
            message_send_error: '📤',
            message_receive_error: '📥',
            network_error: '🌐',
            server_error: '🖥️',
            validation_error: '⚠️',
            memory_error: '🧠',
            processing_error: '⚙️',
            unknown_error: '❓'
        };
        
        return icons[errorType] || icons.unknown_error;
    }

    /**
     * Get error title based on type
     */
    getErrorTitle(errorType) {
        const titles = {
            api_key_invalid: 'Erreur de Configuration',
            api_tokens_depleted: 'Crédits Épuisés',
            stream_error: 'Erreur de Connexion',
            message_send_error: 'Erreur d\'Envoi',
            message_receive_error: 'Erreur de Réception',
            network_error: 'Erreur Réseau',
            server_error: 'Erreur Serveur',
            validation_error: 'Erreur de Validation',
            memory_error: 'Erreur de Mémoire',
            processing_error: 'Erreur de Traitement',
            unknown_error: 'Erreur Inconnue'
        };
        
        return titles[errorType] || titles.unknown_error;
    }

    /**
     * Fade out and remove error element
     */
    fadeOutAndRemove(element) {
        element.style.transition = 'opacity 0.5s ease-out';
        element.style.opacity = '0';
        
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 500);
    }

    /**
     * Clear all error messages
     */
    clearErrors(containerId = 'chat-messages') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const errorElements = container.querySelectorAll('.error-message-bubble');
        errorElements.forEach(element => {
            element.remove();
        });
    }

    /**
     * Handle API error responses
     */
    handleAPIError(response, containerId = 'chat-messages') {
        if (response.error) {
            this.displayError(response, containerId);
            return true;
        }
        return false;
    }

    /**
     * Handle network errors
     */
    handleNetworkError(error, containerId = 'chat-messages') {
        const errorData = {
            error_type: 'network_error',
            severity: 'medium',
            user_message: '🌐 Problème de connexion réseau. Vérifiez votre connexion internet.',
            technical_details: error.message || 'Network error occurred'
        };
        
        this.displayError(errorData, containerId);
    }

    /**
     * Handle stream errors
     */
    handleStreamError(error, containerId = 'chat-messages') {
        const errorData = {
            error_type: 'stream_error',
            severity: 'medium',
            user_message: '📡 Problème de connexion avec l\'agent. Veuillez rafraîchir la page et réessayer.',
            technical_details: error.message || 'Stream error occurred'
        };
        
        this.displayError(errorData, containerId);
    }
}

// Create global instance
window.errorMessage = new ErrorMessage();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorMessage;
} 