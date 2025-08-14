/**
 * Chat Core Module for ASIA.fr Agent Frontend
 */

// Only create if not already defined
if (typeof ChatCore === 'undefined') {
    let ChatCore = {
        isSending: false,
        isAITyping: false,
        eventListenersAttached: false,
        typingSoundEnabled: false,
        typingAudioContext: null,
        conversationId: null,
        API_BASE_URL: '/api',
        initialized: false, // Add initialized flag

        init: async function() {
            // Prevent duplicate initialization
            if (this.initialized) {
                console.log('⚠️ ChatCore already initialized, skipping...');
                return;
            }
            
            console.log('🚀 Initializing ChatCore...');
            
            // Check if chat area exists
            const chatArea = document.querySelector('.chat-messages');
            console.log('🔍 Chat area found during init:', chatArea);
            
            // Set default API config immediately
            this.API_BASE_URL = '/api';
            console.log('🔧 Using default API config:', this.API_BASE_URL);
            
            // Initialize UI components immediately
            this.addBackupModelDashboardButton();
            this.initializeStreamingPlaceholder();
            this.attachEventListeners();
            
            // Try to update API config in background (non-blocking)
            this.updateApiConfig().catch(error => {
                console.warn('⚠️ Failed to update API config:', error);
            });
            
            // Clear memory in background (non-blocking)
            this.clearMemory().catch(error => {
                console.warn('⚠️ Failed to clear memory:', error);
            });
            
            this.initialized = true;
            console.log('✅ Chat core initialized successfully');
        },

        updateApiConfig: async function() {
            console.log('🔧 Updating API config...');
            
            // Quick check if UnifiedConfig is already loaded
            if (window.UnifiedConfig && window.UnifiedConfig.loaded && window.UnifiedConfig.config) {
                const config = window.UnifiedConfig.config;
                if (config && config.api && config.api.base_url) {
                    this.API_BASE_URL = config.api.base_url;
                    console.log('🔧 Updated API config from unified config:', this.API_BASE_URL);
                    return true;
                }
            }
            
            // If not loaded, try to load it once
            if (window.UnifiedConfig) {
                try {
                    await window.UnifiedConfig.loadConfig();
                    const config = window.UnifiedConfig.config;
                    if (config && config.api && config.api.base_url) {
                        this.API_BASE_URL = config.api.base_url;
                        console.log('🔧 Updated API config from unified config:', this.API_BASE_URL);
                        return true;
                    }
                } catch (error) {
                    console.warn('⚠️ Failed to load UnifiedConfig:', error);
                }
            }
            
            // Fallback to default
            this.API_BASE_URL = '/api';
            console.log('🔧 Using fallback API config:', this.API_BASE_URL);
            return true;
        },

        addBackupModelDashboardButton: function() {
            const chatHeader = document.querySelector('.chat-header');
            if (chatHeader && !document.getElementById('backup-model-btn')) {
                const button = document.createElement('button');
                button.id = 'backup-model-btn';
                button.className = 'bg-blue-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-blue-700 transition-colors ml-2';
                button.innerHTML = '🤖 Models';
                button.title = 'Backup Model Dashboard';
                
                button.addEventListener('click', () => {
                    if (window.BackupModelDashboard) {
                        window.BackupModelDashboard.toggle();
                    }
                });
                
                chatHeader.appendChild(button);
            }
        },

        attachEventListeners: function() {
            if (this.eventListenersAttached) return;
            
            const chatInput = document.querySelector('#chat-input');
            const sendButton = document.querySelector('#chat-send-btn');
            const chatForm = document.querySelector('#chat-form');
            
            console.log('🔍 Chat elements found:', {
                chatInput: !!chatInput,
                sendButton: !!sendButton,
                chatForm: !!chatForm
            });
            
            if (chatInput && sendButton) {
                // Prevent form submission from causing page refresh
                if (chatForm) {
                    chatForm.addEventListener('submit', (e) => {
                        console.log('🚫 Form submit prevented');
                        e.preventDefault();
                        this.sendMessage();
                    });
                }
                
                // Send button click
                sendButton.addEventListener('click', (e) => {
                    console.log('🚫 Button click prevented');
                    e.preventDefault();
                    this.sendMessage();
                });
                
                // Enter key press
                chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        console.log('🚫 Enter key prevented');
                        e.preventDefault();
                        this.sendMessage();
                    }
                });
                
                // Input change for visual feedback
                chatInput.addEventListener('input', () => this.updateSendButtonState());
                
                // Start input placeholder cycling
                this.startInputPlaceholderCycling(chatInput);
                
                this.eventListenersAttached = true;
                console.log('[DEBUG] Attaching chat event listeners');
            } else {
                console.warn('⚠️ Chat elements not found, cannot attach event listeners');
            }
        },

        sendMessage: async function() {
            console.log('📤 sendMessage called');
            const chatInput = document.querySelector('#chat-input');
            const message = chatInput?.value?.trim();
            
            console.log('📝 Message content:', message);
            console.log('🔍 Current state:', {
                isSending: this.isSending,
                isAITyping: this.isAITyping
            });
            
            if (!message || this.isSending || this.isAITyping) {
                console.log('❌ sendMessage blocked:', {
                    noMessage: !message,
                    isSending: this.isSending,
                    isAITyping: this.isAITyping
                });
                return;
            }
            
            console.log('[DEBUG] sendMessage called, message:', message);
            
            // Clear input and update state
            chatInput.value = '';
            this.isSending = true;
            this.updateSendButtonState();
            
            // Create conversation ID if not exists
            if (!this.conversationId) {
                this.conversationId = 'conv_' + Date.now();
                console.log('[DEBUG] Created new conversation ID:', this.conversationId);
            } else {
                console.log('[DEBUG] Using existing conversation ID:', this.conversationId);
            }
            
            // Add user message to chat
            console.log('📝 Adding user message to chat...');
            this.appendMessage(message, true);
            
            // Show AI typing immediately
            console.log('🤖 Showing AI typing immediately...');
            this.isAITyping = true;
            this.updateSendButtonState();
            
            // Create streaming placeholder immediately
            const streamingElement = this.appendMessage('', false, false, true);
            console.log('🔄 Created streaming element:', streamingElement);
            console.log('🔍 Streaming element details:', {
                element: streamingElement,
                hasMessageText: streamingElement?.querySelector('.message-text'),
                innerHTML: streamingElement?.innerHTML
            });
            
            // Send to API
            console.log('🌐 Sending to API...');
            await this.sendToAPI(message, streamingElement);
            
            // Reset state
            this.isSending = false;
            this.isAITyping = false;
            this.updateSendButtonState();
        },

        sendToAPI: async function(message, streamingElement = null) {
            console.log('🚀 Starting to send message:', message);
            console.log('🔧 Using API URL:', this.API_BASE_URL);
            console.log('🔄 Streaming element passed to sendToAPI:', streamingElement);
            
            try {
                const fullUrl = `${this.API_BASE_URL}/chat/stream`;
                console.log('🌐 Making request to:', fullUrl);
                
                const response = await fetch(fullUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        conversation_id: this.conversationId,
                        user_id: '1'
                    })
                });

                console.log('📡 Response status:', response.status);
                console.log('📡 Response headers:', response.headers);
                console.log('📡 Content-Type:', response.headers.get('content-type'));
                console.log('📡 Response body type:', response.body ? 'ReadableStream' : 'No body');

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                console.log('✅ Streaming response received, processing...');
                console.log('🔄 About to call processStreamingResponse with streamingElement:', streamingElement);
                
                await this.processStreamingResponse(response, streamingElement);
                console.log('✅ processStreamingResponse completed');
                
            } catch (error) {
                console.error('❌ Error sending message:', error);
                this.appendMessage('Désolé, une erreur s\'est produite. Veuillez réessayer.', false, true);
            }
        },

        processStreamingResponse: async function(response, streamingElement = null) {
            console.log('🔄 Processing streaming response, streamingElement:', streamingElement);
            console.log('📡 Response body available:', !!response.body);
            
            if (!response.body) {
                console.error('❌ No response body available for streaming');
                return;
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let fullResponse = '';
            
            // Use provided streaming element or create new one
            if (!streamingElement) {
                console.log('⚠️ No streaming element provided, creating new one...');
                streamingElement = this.appendMessage('', false, false, true);
            }
            const textElement = streamingElement?.querySelector('.message-text');
            console.log('🔍 Text element found:', textElement);
            
            // Clear the streaming placeholder and start with empty content
            if (textElement) {
                textElement.textContent = '';
                textElement.classList.add('streaming-active');
            }
            
            try {
                console.log('🔄 Starting to read stream...');
                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) {
                        console.log('✅ Stream reader done');
                        break;
                    }
                    
                    const chunk = decoder.decode(value, { stream: true });
                    buffer += chunk;
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || '';
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            
                                                             if (data === '[DONE]') {
                                     console.log('✅ Streaming completed');
                                     // Replace streaming placeholder with final message
                                     if (textElement && fullResponse) {
                                         textElement.innerHTML = this.formatMessage(fullResponse);
                                         textElement.classList.remove('streaming', 'streaming-active');
                                     }
                                     break;
                                 }
                            
                            try {
                                const parsed = JSON.parse(data);
                                
                                                                             if (parsed.type === 'offers' && parsed.offers) {
                console.log('🎯 Received offers data:', parsed.offers);
                // Display offers using the confirmation flow card system
                if (window.confirmationFlow) {
                    window.confirmationFlow.displayOffers(parsed.offers);
                }
            } else if (parsed.type === 'content' && textElement) {
                                     fullResponse += parsed.chunk;
                                     // Use textContent for streaming to show word-by-word effect
                                     textElement.textContent = fullResponse;
                                     console.log('📝 Updated streaming content:', fullResponse);
                                     
                                     // Add a small delay to make streaming more visible
                                     await new Promise(resolve => setTimeout(resolve, 50));
                                 } else if (parsed.type === 'end') {
                                     console.log('✅ Streaming ended');
                                     // Replace streaming placeholder with final message
                                     if (textElement && fullResponse) {
                                         textElement.innerHTML = this.formatMessage(fullResponse);
                                         textElement.classList.remove('streaming', 'streaming-active');
                                     }
                                     
                                     // No confirmation dialog - AI handles everything
                                     console.log('🎯 AI agent handles all confirmation logic - no UI needed');
                                     break;
                                 }
                            } catch (e) {
                                console.warn('⚠️ Error parsing JSON:', e, 'Data:', data);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('❌ Error processing stream:', error);
            } finally {
                reader.releaseLock();
            }
        },

        appendMessage: function(message, isUser = false, isError = false, shouldStream = false) {
            const chatArea = document.querySelector('.chat-messages');
            console.log('🔍 Looking for chat area:', chatArea);
            if (!chatArea) {
                console.warn('⚠️ Chat area not found (.chat-messages)');
                return null;
            }
            
            console.log('📝 Appending message:', { message, isUser, isError, shouldStream });
            
            // Use Twig template for message rendering
            const messageHtml = this.renderMessageTemplate(message, isUser, isError, shouldStream);
            console.log('📝 Generated HTML:', messageHtml);
            
            if (shouldStream) {
                // For streaming, create element and return it
                const msgDiv = document.createElement('div');
                msgDiv.innerHTML = messageHtml;
                const firstChild = msgDiv.firstElementChild;
                console.log('🔄 Created streaming element:', firstChild);
                console.log('🔍 Streaming element HTML:', firstChild?.innerHTML);
                chatArea.appendChild(firstChild);
                chatArea.scrollTop = chatArea.scrollHeight;
                
                return firstChild;
            } else {
                // For regular messages, append directly
                chatArea.insertAdjacentHTML('beforeend', messageHtml);
                chatArea.scrollTop = chatArea.scrollHeight;
            }
            
            return null;
        },

        renderMessageTemplate: function(message, isUser, isError, shouldStream) {
            // This would be replaced with actual Twig template rendering
            // For now, we'll keep the existing HTML structure
            if (isUser) {
                return `
                    <div class="flex justify-end mb-6">
                        <div class="bg-chat-user shadow-theme-xs rounded-3xl rounded-tr-lg py-4 px-5 max-w-md" style="background-color: #8B0000 !important;">
                            <p class="text-white dark:text-white/90 font-normal">
                                ${message.replace(/\n/g, '<br>')}
                            </p>
                        </div>
                    </div>
                `;
            } else {
                const errorClass = isError ? 'bg-red-100 dark:bg-red-500 text-red-700 dark:text-white' : 'bg-chat-ai bg-white dark:bg-white/5';
                
                if (shouldStream) {
                    return `
                        <div class="flex justify-start mb-6">
                            <div class="${errorClass} shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl">
                                <p class="text-gray-800 dark:text-white/90 font-normal message-text streaming" style="opacity: 0.8;">
                                    <span class="spinner" style="display: inline-block; width: 16px; height: 16px; border: 2px solid #f3f3f3; border-top: 2px solid #ff0000; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px;"></span>
                                    L'IA prépare votre réponse...
                                </p>
                            </div>
                        </div>
                    `;
                } else {
                    return `
                        <div class="flex justify-start mb-6">
                            <div class="${errorClass} shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl">
                                <p class="text-gray-800 dark:text-white/90 font-normal">
                                    ${this.formatMessage(message)}
                                </p>
                            </div>
                        </div>
                    `;
                }
            }
        },

        formatMessage: function(message) {
            if (message.includes('•')) {
                const parts = message.split('•');
                const intro = parts[0].trim();
                const bulletPoints = parts.slice(1).map(point => point.trim()).filter(point => point);
                
                let html = '';
                if (intro) {
                    html += `<div class="mb-3">${intro}</div>`;
                }
                
                if (bulletPoints.length > 0) {
                    html += '<ul class="list-none space-y-2 mt-3">';
                    bulletPoints.forEach(point => {
                        html += `<li class="flex items-start">
                            <span class="text-gray-600 dark:text-gray-400 mr-2 mt-1">•</span>
                            <span>${point}</span>
                        </li>`;
                    });
                    html += '</ul>';
                }
                
                return html;
            } else {
                return message.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');
            }
        },

        updateSendButtonState: function() {
            const sendButton = document.querySelector('#chat-send-btn');
            const chatInput = document.querySelector('#chat-input');
            
            if (!sendButton || !chatInput) return;
            
            const hasText = chatInput.value.trim().length > 0;
            const canSend = hasText && !this.isSending && !this.isAITyping;
            
            // Update send button state
            sendButton.disabled = !canSend;
            sendButton.style.opacity = canSend ? '1' : '0.5';
            sendButton.style.cursor = canSend ? 'pointer' : 'not-allowed';
            
            // Update input field state
            chatInput.disabled = this.isSending || this.isAITyping;
            chatInput.style.opacity = (this.isSending || this.isAITyping) ? '0.5' : '1';
            chatInput.style.cursor = (this.isSending || this.isAITyping) ? 'not-allowed' : 'text';
        },

        clearMemory: async function() {
            try {
                // Use the correct endpoint from configuration
                const endpoint = window.UnifiedConfig?.config?.api?.endpoints?.memory_clear || '/memory/clear';
                const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_id: 1 })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                console.log('🧹 Memory cleared successfully');
            } catch (error) {
                console.warn('⚠️ Failed to clear memory:', error);
            }
        },

        initializeStreamingPlaceholder: function() {
            // Add CSS for streaming placeholder effect and spinner
            const style = document.createElement('style');
            style.innerHTML = `
                .streaming-placeholder {
                    opacity: 0.6;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 0.6; }
                    50% { opacity: 0.8; }
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .spinner {
                    display: inline-block;
                    width: 16px;
                    height: 16px;
                    border: 2px solid #f3f3f3;
                    border-top: 2px solid #ff0000;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                .streaming-active {
                    /* Removed red border for cleaner look */
                }
            `;
            document.head.appendChild(style);
        },

        checkForConfirmationInResponse: function(response) {
            // This is now handled by the AI agent - no need for JavaScript extraction
            console.log('🎯 AI agent handles all preference extraction and confirmation logic');
        },

        startInputPlaceholderCycling: function(chatInput) {
            const placeholders = [
                "Dites-moi où vous voulez partir ou ce que vous cherchez...",
                "Je veux aller au Japon pour 2 semaines",
                "Budget moyen pour une aventure culturelle",
                "Philippines en famille pour 10 jours",
                "Voyage de luxe en Thaïlande",
                "Backpacking au Vietnam",
                "Retraite spirituelle en Inde",
                "Croisière en Asie du Sud-Est",
                "Tour gastronomique en Corée",
                "Aventure en Mongolie",
                "Détente aux Maldives"
            ];
            
            let currentPlaceholderIndex = 0;
            let currentText = '';
            let isTyping = true;
            let typingSpeed = 100; // ms per character
            let deletingSpeed = 50; // ms per character
            
            const typeText = async (text) => {
                for (let i = 0; i <= text.length; i++) {
                    if (!chatInput || chatInput.value !== '') {
                        // User started typing, stop cycling
                        return;
                    }
                    chatInput.placeholder = text.substring(0, i);
                    await new Promise(resolve => setTimeout(resolve, typingSpeed));
                }
            };
            
            const deleteText = async (text) => {
                for (let i = text.length; i >= 0; i--) {
                    if (!chatInput || chatInput.value !== '') {
                        // User started typing, stop cycling
                        return;
                    }
                    chatInput.placeholder = text.substring(0, i);
                    await new Promise(resolve => setTimeout(resolve, deletingSpeed));
                }
            };
            
            const cyclePlaceholders = async () => {
                if (!chatInput || chatInput.value !== '') {
                    // User is typing, don't cycle
                    return;
                }
                
                const placeholder = placeholders[currentPlaceholderIndex];
                
                // Type the placeholder
                await typeText(placeholder);
                
                // Wait a bit
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Delete the placeholder
                await deleteText(placeholder);
                
                // Move to next placeholder
                currentPlaceholderIndex = (currentPlaceholderIndex + 1) % placeholders.length;
            };
            
            // Start the cycling
            const startCycling = () => {
                cyclePlaceholders().then(() => {
                    if (chatInput && chatInput.value === '') {
                        // Continue cycling if user hasn't typed
                        setTimeout(startCycling, 500);
                    }
                });
            };
            
            // Start cycling after a delay
            setTimeout(startCycling, 1000);
        }
    };

    // Make available globally
    window.chatCore = ChatCore;
    console.log('📦 ChatCore module loaded and exported to window.chatCore');
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            if (!ChatCore.initialized) {
                ChatCore.init();
            }
        });
    } else {
        if (!ChatCore.initialized) {
            ChatCore.init();
        }
    }
} 