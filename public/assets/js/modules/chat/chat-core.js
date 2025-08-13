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
        API_BASE_URL: 'http://localhost:8000',

        init: async function() {
            // Initialize unified configuration first
            if (window.UnifiedConfig) {
                await window.UnifiedConfig.load();
                await this.updateApiConfig();
            }
            
            // Add backup model dashboard button
            this.addBackupModelDashboardButton();
            
            // Clear memory on page load/refresh
            try {
                await this.clearMemory();
            } catch (error) {
                console.warn('⚠️ Failed to clear memory on page load:', error);
            }
            
            // Initialize streaming placeholder effect
            this.initializeStreamingPlaceholder();
            
            // Attach event listeners
            this.attachEventListeners();
        },

        updateApiConfig: async function() {
            console.log('🔧 Updating API config...');
            console.log('UnifiedConfig loaded:', window.UnifiedConfig?.loaded);
            console.log('UnifiedConfig config:', window.UnifiedConfig?.config);
            
            if (window.UnifiedConfig && window.UnifiedConfig.loaded) {
                const config = window.UnifiedConfig.config;
                console.log('Config received:', config);
                if (config && config.api && config.api.base_url) {
                    this.API_BASE_URL = config.api.base_url;
                    console.log('🔧 Updated API config from unified config:', this.API_BASE_URL);
                } else {
                    console.warn('⚠️ No API base_url found in config');
                }
            } else {
                console.warn('⚠️ UnifiedConfig not loaded yet');
            }
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
            
            // Send to API
            console.log('🌐 Sending to API...');
            await this.sendToAPI(message);
            
            // Reset state
            this.isSending = false;
            this.updateSendButtonState();
        },

        sendToAPI: async function(message) {
            console.log('🚀 Starting to send message:', message);
            console.log('🔧 Using API URL:', this.API_BASE_URL);
            
            // Set AI typing state
            this.isAITyping = true;
            this.updateSendButtonState();
            
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

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                console.log('✅ Streaming response received, processing...');
                await this.processStreamingResponse(response);
                
            } catch (error) {
                console.error('❌ Error sending message:', error);
                this.appendMessage('Désolé, une erreur s\'est produite. Veuillez réessayer.', false, true);
            } finally {
                // Reset AI typing state
                this.isAITyping = false;
                this.updateSendButtonState();
            }
        },

        processStreamingResponse: async function(response) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            // Create streaming message element
            const streamingElement = this.appendMessage('', false, false, true);
            const textElement = streamingElement?.querySelector('.message-text');
            
            try {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || '';
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data === '[DONE]') {
                                console.log('✅ Streaming completed');
                                // Remove streaming placeholder and show final message
                                if (textElement) {
                                    textElement.innerHTML = textElement.textContent;
                                    textElement.classList.remove('streaming');
                                }
                                break;
                            }
                            
                            try {
                                const parsed = JSON.parse(data);
                                if (parsed.type === 'content' && textElement) {
                                    textElement.textContent += parsed.chunk;
                                } else if (parsed.type === 'end') {
                                    console.log('✅ Streaming ended');
                                    // Remove streaming placeholder and show final message
                                    if (textElement) {
                                        textElement.innerHTML = textElement.textContent;
                                        textElement.classList.remove('streaming');
                                    }
                                    break;
                                }
                            } catch (e) {
                                // Ignore parsing errors for incomplete JSON
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
            if (!chatArea) {
                console.warn('⚠️ Chat area not found (.chat-messages)');
                return null;
            }
            
            console.log('📝 Appending message:', { message, isUser, isError, shouldStream });
            
            // Use Twig template for message rendering
            const messageHtml = this.renderMessageTemplate(message, isUser, isError, shouldStream);
            
            if (shouldStream) {
                // For streaming, create element and return it
                const msgDiv = document.createElement('div');
                msgDiv.innerHTML = messageHtml;
                chatArea.appendChild(msgDiv.firstElementChild);
                return msgDiv.firstElementChild;
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
                                    <span class="spinner" style="display: inline-block; width: 16px; height: 16px; border: 2px solid #f3f3f3; border-top: 2px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px;"></span>
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
                const response = await fetch(`${this.API_BASE_URL}/chat/memory/clear`, {
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
                    border-top: 2px solid #3498db;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
            `;
            document.head.appendChild(style);
        }
    };

    // Make available globally
    window.chatCore = ChatCore;
    console.log('📦 ChatCore module loaded and exported to window.chatCore');
} 