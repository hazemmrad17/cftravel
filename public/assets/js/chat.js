// Chat logic with session and conversation state management

// Global flag to prevent multiple simultaneous sends
let isSending = false;
let eventListenersAttached = false;

document.addEventListener('DOMContentLoaded', function() {
  // Add custom styling for chat messages
  const style = document.createElement('style');
  style.innerHTML = `
    .loader { 
      border: 3px solid #f3f3f3; 
      border-top: 3px solid #7F68FF; 
      border-radius: 50%; 
      width: 18px; 
      height: 18px; 
      animation: spin 1s linear infinite; 
      display: inline-block; 
    } 
    @keyframes spin { 
      0% { transform: rotate(0deg); } 
      100% { transform: rotate(360deg); } 
    }

    .chat-area {
      scroll-behavior: smooth;
    }

    .chat-messages {
      scroll-behavior: smooth;
    }
    .chat-messages::-webkit-scrollbar {
      width: 6px;
    }
    .chat-messages::-webkit-scrollbar-track {
      background: transparent;
    }
    .chat-messages::-webkit-scrollbar-thumb {
      background: rgba(156, 163, 175, 0.5);
      border-radius: 3px;
    }
    .chat-messages::-webkit-scrollbar-thumb:hover {
      background: rgba(156, 163, 175, 0.8);
    }
  `;
  document.head.appendChild(style);

  // Menu open/close logic
  document.body.addEventListener('click', function (e) {
    // Open menu
    if (e.target.closest('[data-action="menu"]')) {
      e.preventDefault();
      const menuBtn = e.target.closest('[data-action="menu"]');
      const menuDropdown = menuBtn.parentElement.querySelector('.menu-dropdown');
      // Close all other menus
      document.querySelectorAll('.menu-dropdown').forEach(d => d.classList.add('hidden'));
      if (menuDropdown) menuDropdown.classList.toggle('hidden');
      return;
    }
    // Click outside closes all menus
    if (!e.target.closest('.menu-dropdown')) {
      document.querySelectorAll('.menu-dropdown').forEach(d => d.classList.add('hidden'));
    }
    // Rename logic
    if (e.target.closest('[data-action="rename"]')) {
      e.preventDefault();
      const btn = e.target.closest('[data-action="rename"]');
      const row = btn.closest('.chat-sidebar-item');
      const titleLink = row.querySelector('a');
      const oldTitle = titleLink.textContent.trim();
      const convId = row.getAttribute('data-conversation-id');
      // Replace title with input
      const input = document.createElement('input');
      input.type = 'text';
      input.value = oldTitle;
      input.className = 'w-full px-2 py-1 rounded';
      titleLink.replaceWith(input);
      input.focus();
      input.select();
      input.addEventListener('keydown', function(ev) {
        if (ev.key === 'Enter') {
          ev.preventDefault();
          saveTitle();
        } else if (ev.key === 'Escape') {
          input.replaceWith(titleLink);
        }
      });
      input.addEventListener('blur', function() {
        saveTitle();
      });
      function saveTitle() {
        const newTitle = input.value.trim();
        if (newTitle && newTitle !== oldTitle) {
                fetch(`/chat/conversation/${convId}/title`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        body: JSON.stringify({ title: newTitle })
      })
      .then(r => {
        return r.json();
      })
      .then(data => {
        if (data.success) {
          titleLink.textContent = newTitle;
        }
        input.replaceWith(titleLink);
      })
      .catch(error => {
        console.error('Erreur de renommage:', error);
        alert('Désolé, il y a eu un problème lors du renommage. Veuillez réessayer.');
        input.replaceWith(titleLink);
      });
        } else {
          input.replaceWith(titleLink);
        }
      }
      // Close menu
      row.querySelector('.menu-dropdown').classList.add('hidden');
      return;
    }
    // Delete logic
    if (e.target.closest('[data-action="delete"]')) {
      e.preventDefault();
      if (!confirm('Êtes-vous sûr de vouloir supprimer cette conversation ? Cette action ne peut pas être annulée.')) return;
      const btn = e.target.closest('[data-action="delete"]');
      const row = btn.closest('.chat-sidebar-item');
      const convId = row.getAttribute('data-conversation-id');
      fetch(`/chat/conversation/${convId}/delete`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(r => {
        return r.json();
      })
      .then(data => {
        if (data.success) {
          // Remove the deleted conversation from the UI
          row.parentElement.removeChild(row);
          
          // Check if we're currently viewing the deleted conversation
          const currentConvId = getCurrentConversationId();
          if (currentConvId === convId) {
            // Find the first available conversation in the sidebar
            const remainingConversations = document.querySelectorAll('.chat-sidebar-item');
            if (remainingConversations.length > 0) {
              // Get the first conversation's ID
              const firstConversation = remainingConversations[0];
              const firstConvId = firstConversation.getAttribute('data-conversation-id');
              
              // Redirect to the first conversation
              window.location.href = `/chat/${agent || 'tentatio'}/${firstConvId}`;
            } else {
              // No conversations left, redirect to new chat
              window.location.href = '/chat/new';
            }
          }
        }
      })
      .catch(error => {
        console.error('Erreur de suppression:', error);
        alert('Désolé, il y a eu un problème lors de la suppression. Veuillez réessayer.');
      });
      return;
    }
  });

  const chatForm = document.getElementById('chat-form');
  if (!chatForm) return;

  const agent = chatForm.dataset.agent;
  const chatInput = document.getElementById('chat-input');
  const sendButton = document.getElementById('chat-send-btn');
  const chatArea = document.querySelector('.p-5.py-12');
  if (chatArea) {
    chatArea.classList.add('chat-area');
  }
  let loadingMsgDiv = null;

  // Database-based conversation management system
  let currentConversationId = null;
  
  function getCurrentConversationId() {
    if (!currentConversationId) {
      // Try to get from URL first
      const urlParams = new URLSearchParams(window.location.search);
      const convId = urlParams.get('conversation_id');
      
      if (convId) {
        currentConversationId = convId;
      } else {
        // Get from the current page URL path
        const pathParts = window.location.pathname.split('/');
        const conversationIdFromPath = pathParts[pathParts.length - 1];
        
        if (conversationIdFromPath && !isNaN(conversationIdFromPath)) {
          currentConversationId = conversationIdFromPath;
        } else {
          // Try to find conversation ID in the path (for URLs like /chat/tentatio/14)
          for (let i = pathParts.length - 1; i >= 0; i--) {
            const part = pathParts[i];
            if (part && !isNaN(part)) {
              currentConversationId = part;
              break;
            }
          }
        }
      }
    }
    return currentConversationId;
  }

  async function loadConversationFromDatabase(conversationId) {
    try {
      const response = await fetch(`/api/conversation/${conversationId}/messages`);
      
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        console.error('Failed to load conversation:', response.status);
        const errorText = await response.text();
        console.error('Error response:', errorText);
        return null;
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
      return null;
    }
  }

  async function saveMessageToDatabase(conversationId, content, role = 'user', sender = 'user') {
    try {
      const response = await fetch(`/api/conversation/${conversationId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content,
          role: role,
          sender: sender
        })
      });
      if (response.ok) {
        const data = await response.json();
        return data.success;
      } else {
        console.error('Failed to save message:', response.status);
        return false;
      }
    } catch (error) {
      console.error('Error saving message:', error);
      return false;
    }
  }

  async function createNewConversation() {
    // Clear memory first
    await clearMemory();
    
    // Clear the chat area
    const chatArea = document.querySelector('.p-5.py-12');
    if (chatArea) {
      chatArea.innerHTML = '';
    }
    
    // Reset conversation ID
    currentConversationId = null;
    
    // Update URL to remove conversation ID
    const url = new URL(window.location);
    url.searchParams.delete('conversation_id');
    window.history.pushState({}, '', url);
    
    // Show welcome message from agent
    showWelcomeMessage();
    
    // Focus on input
    if (chatInput) {
      chatInput.focus();
    }
  }

  async function clearMemory() {
    try {
      const response = await fetch('/chat/memory/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        console.log('✅ Memory cleared successfully');
      } else {
        console.warn('⚠️ Failed to clear memory:', response.status);
      }
    } catch (error) {
      console.warn('⚠️ Error clearing memory:', error);
    }
  }

  async function switchToConversation(conversationId) {
    currentConversationId = conversationId;
    
    // Update URL
    const url = new URL(window.location);
    url.searchParams.set('conversation_id', conversationId);
    window.history.pushState({}, '', url);
    
    // Load and render the conversation
    await renderConversationHistory();
  }

  // Handle conversation clicks in sidebar
  document.addEventListener('click', function(e) {
    if (e.target.closest('.chat-sidebar-item')) {
      const conversationItem = e.target.closest('.chat-sidebar-item');
      const conversationId = conversationItem.getAttribute('data-conversation-id');
      if (conversationId) {
        switchToConversation(conversationId);
  }
    }
  });

  function appendMessage(message, isUser, isError, offers, shouldStream = false) {
    // Remove previous offer cards before rendering new ones
    document.querySelectorAll('.chat-offer-card').forEach(el => el.remove());

    // If offers are present, show only a short intro and the cards
    if (offers && offers.length > 0) {
      // Show a single intro message
      const introDiv = document.createElement('div');
      introDiv.className = 'chat-message agent';
      introDiv.textContent = "Voici quelques offres qui correspondent à votre demande :";
      chatArea.appendChild(introDiv);

      offers.forEach(offer => {
        const offerDiv = document.createElement('div');
        offerDiv.className = 'chat-offer-card';
        let highlightsHtml = '';
        if (offer.highlights && Array.isArray(offer.highlights) && offer.highlights.length > 0) {
          highlightsHtml = '<ul style="margin: 0.5em 0 0.5em 1em;">' +
            offer.highlights.map(h => `<li><strong>${h.title || ''}:</strong> ${h.text || ''}</li>`).join('') +
            '</ul>';
        }
        offerDiv.innerHTML = `
          <div style="margin: 1em 0; padding: 1em; border: 1px solid #eee; border-radius: 8px; background: #fafbff; transition: all 0.2s ease;">
            <strong style="font-size: 1.1em;">${offer.product_name || ''}</strong><br>
            ${highlightsHtml}
            <span>${offer.description || ''}</span><br>
            <a href="${offer.price_url || '#'}" target="_blank" style="color: #7F68FF; text-decoration: none; font-weight: 500;">Voir l'offre</a>
          </div>
        `;
        chatArea.appendChild(offerDiv);
      });
      return; // Do not render the full message if offers are present
    }

    // If no offers, render the message as usual
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex ' + (isUser ? 'justify-end' : 'justify-start') + ' mb-6';
    let html = '';
    
    if (isUser) {
      html = `
        <div class="bg-chat-user shadow-theme-xs rounded-3xl rounded-tr-lg py-4 px-5 max-w-md" style="background-color: #8B0000 !important;">
          <p class="text-white dark:text-white/90 font-normal">
            ${message}
          </p>
        </div>
      `;
      msgDiv.innerHTML = html;
      chatArea.appendChild(msgDiv);
      // Smooth scroll to bottom
      setTimeout(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
      }, 100);
    } else {
      // For AI messages
      if (shouldStream) {
        // Create empty message element for server streaming
        html = `
          <div class="${isError ? 'bg-red-100 dark:bg-red-500 text-red-700 dark:text-white rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl' : 'bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl'}">
          <p class="text-gray-800 dark:text-white/90 font-normal message-text"></p>
        </div>
        `;
        msgDiv.innerHTML = html;
        chatArea.appendChild(msgDiv);
        // Return the message element for streaming updates
        return msgDiv;
      } else {
        // Show immediately for loaded messages (no streaming)
        html = `
          <div class="${isError ? 'bg-red-100 dark:bg-red-500 text-red-700 dark:text-white rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl' : 'bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl'}">
          <p class="text-gray-800 dark:text-white/90 font-normal">${message}</p>
        </div>
        `;
        msgDiv.innerHTML = html;
        chatArea.appendChild(msgDiv);
        // Smooth scroll to bottom
        setTimeout(() => {
          chatArea.scrollTop = chatArea.scrollHeight;
        }, 100);
      }
    }
  }

  function showLoading() {
    // Create typing indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'flex justify-start mb-6';
    loadingDiv.id = 'typing-indicator';
    loadingDiv.innerHTML = `
      <div class="bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl">
        <p class="text-gray-800 dark:text-white/90 font-normal">
          L'IA rédige... <span class="loader"></span>
        </p>
      </div>
    `;
    chatArea.appendChild(loadingDiv);
    
    // Scroll to bottom
    setTimeout(() => {
      chatArea.scrollTop = chatArea.scrollHeight;
    }, 100);
  }

  function hideLoading() {
    // Remove typing indicator
    const loadingDiv = document.getElementById('typing-indicator');
    if (loadingDiv) {
      loadingDiv.remove();
    }
  }



  // Welcome message logic
  function displayOfferCards(offers) {
    const offersContainer = document.createElement('div');
    offersContainer.className = 'flex justify-start mb-6';
    offersContainer.innerHTML = `
      <div class="bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg p-4 max-w-4xl">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          ${offers.map(offer => createOfferCard(offer)).join('')}
        </div>
      </div>
    `;
    chatArea.appendChild(offersContainer);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function createOfferCard(offer) {
    const destinations = offer.destinations.map(d => `${d.city} (${d.country})`).join(', ');
    const highlights = offer.highlights.map(h => h.text).join(', ');
    const imageUrl = offer.images && offer.images.length > 0 ? offer.images[0] : '/assets/images/placeholder-travel.svg';
    
    return `
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-200 dark:border-gray-700">
        <div class="relative">
          <img src="${imageUrl}" alt="${offer.product_name}" class="w-full h-48 object-cover" onerror="this.src='/assets/images/placeholder-travel.svg'">
          <div class="absolute top-2 right-2">
            <span class="bg-red-600 text-white text-xs px-2 py-1 rounded-full font-medium">
              ${offer.duration} jours
            </span>
          </div>
        </div>
        <div class="p-4">
          <h3 class="font-bold text-lg text-gray-900 dark:text-white mb-2 line-clamp-2">
            ${offer.product_name}
          </h3>
          <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 mb-2">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            ${destinations}
          </div>
          <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 mb-3">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            ${offer.departure_city}
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-3">
            ${offer.description}
          </p>
          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
              ${offer.offer_type}
            </span>
            <a href="${offer.price_url || '#'}" target="_blank" class="bg-red-600 hover:bg-red-700 text-white text-sm px-4 py-2 rounded-lg transition-colors duration-200">
              Voir l'offre
            </a>
          </div>
        </div>
      </div>
    `;
  }

  function showWelcomeMessage() {
    // Get welcome message from agent and display it
    getWelcomeMessageFromAgent().then(welcomeMessage => {
      if (welcomeMessage) {
        appendMessage(welcomeMessage, false, false, [], false);
      }
    }).catch(error => {
      console.warn('Failed to get welcome message from agent:', error);
      // Focus on input as fallback
      setTimeout(() => {
        if (chatInput) {
          chatInput.focus();
        }
      }, 500);
    });
  }

  async function getWelcomeMessageFromAgent() {
    try {
      const response = await fetch('/chat/welcome', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.message;
      } else {
        console.warn('Failed to get welcome message:', response.status);
        return null;
      }
    } catch (error) {
      console.warn('Error getting welcome message:', error);
      return null;
    }
  }

  function updateStreamingMessage(messageElement, content) {
    // Update the message content with streaming text
    const textElement = messageElement.querySelector('.message-text');
    if (textElement) {
      textElement.textContent = content;
      // Scroll to bottom as content updates
      setTimeout(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
      }, 50);
    }
  }

  function finalizeStreamingMessage(messageElement, content) {
    // Finalize the streaming message
    const textElement = messageElement.querySelector('.message-text');
    if (textElement) {
      textElement.textContent = content;
      // Remove any streaming indicators
      textElement.classList.remove('streaming');
      // Final scroll to bottom
      setTimeout(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
      }, 100);
    }
  }

  // Render conversation history from database
  async function renderConversationHistory() {
    chatArea.innerHTML = '';
    const conversationId = getCurrentConversationId();
    
    if (!conversationId) {
      showWelcomeMessage();
      return;
    }
    
    const conversationData = await loadConversationFromDatabase(conversationId);
    
    if (conversationData && conversationData.messages && conversationData.messages.length > 0) {
      conversationData.messages.forEach(message => {
        if (message.role === 'user') {
          appendMessage(message.content, true, false, [], false); // No streaming for loaded messages
        } else if (message.role === 'assistant') {
          appendMessage(message.content, false, false, [], false); // No streaming for loaded messages
        }
      });
    } else {
      showWelcomeMessage();
    }
  }

  async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Prevent multiple simultaneous sends with more robust checking
    if (isSending) {
      console.log('🚫 Message already being sent, ignoring new request');
      return;
    }
    
    console.log('🚀 Starting to send message:', message);
    isSending = true;
    
    // Add a safety timeout to reset the flag if something goes wrong
    const safetyTimeout = setTimeout(() => {
      if (isSending) {
        console.warn('⚠️ Safety timeout triggered, resetting send state');
        isSending = false;
        chatInput.disabled = false;
        sendButton.disabled = false;
        hideLoading();
      }
    }, 30000); // 30 seconds timeout
    
    // Disable input and button while sending
    chatInput.disabled = true;
    sendButton.disabled = true;
    
    const conversationId = getCurrentConversationId();
    if (!conversationId) {
      console.error('❌ No conversation ID available');
      isSending = false;
      chatInput.disabled = false;
      sendButton.disabled = false;
      return;
    }
    
    // Save user message to database
    const userMessageSaved = await saveMessageToDatabase(conversationId, message, 'user', 'user');
    if (!userMessageSaved) {
      console.error('❌ Failed to save user message');
      isSending = false;
      chatInput.disabled = false;
      sendButton.disabled = false;
      return;
    }
    
    appendMessage(message, true, false, [], false); // No streaming for user messages
    chatInput.value = '';
    
    // Remove any existing loading indicators before showing new one
    hideLoading();
    showLoading();
    
    // Clear input and focus for next message
    setTimeout(() => {
      chatInput.focus();
    }, 100);
    
    try {
      console.log('📡 Attempting streaming request...');
      // Try streaming first, fallback to regular API
      const streamResponse = await fetch(`/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId,
          user_id: 1
        }),
      });
      
      if (streamResponse.ok) {
        console.log('✅ Streaming response received, processing...');
        // Use streaming response
        const reader = streamResponse.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = '';
        
        // Remove loading indicator and create assistant message element for streaming
        hideLoading();
        const assistantMessageElement = appendMessage('', false, false, [], true);
        
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            console.log('📦 Received streaming chunk:', chunk);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  console.log('📊 Parsed streaming data:', data);
                  
                  if (data.type === 'content' && data.chunk) {
                    assistantMessage += data.chunk;
                    // Update the message element with new content
                    updateStreamingMessage(assistantMessageElement, assistantMessage);
                  } else if (data.type === 'end') {
                    // Streaming finished
                    console.log('✅ Streaming completed');
                    finalizeStreamingMessage(assistantMessageElement, assistantMessage);
                    
                    // Save assistant message to database
                    const assistantMessageSaved = await saveMessageToDatabase(conversationId, assistantMessage, 'assistant', 'agent');
                    if (!assistantMessageSaved) {
                      console.error('❌ Failed to save assistant message');
                    }
                    return;
                  } else if (data.type === 'error') {
                    console.error('❌ Streaming error:', data.error);
                    appendMessage('Désolé, je rencontre des difficultés techniques. Veuillez réessayer.', false, true, [], false);
                    return;
                  }
                } catch (e) {
                  console.warn('⚠️ Error parsing streaming data:', e);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      } else {
        console.log('⚠️ Streaming failed, falling back to regular API');
        // Fallback to regular API
        const resp = await fetch(`/chat/message`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: message,
            conversation_id: conversationId,
            user_id: 1
          }),
        });
        
        hideLoading();
        if (resp.ok) {
          const data = await resp.json();
          
          // Get assistant response
          const assistantMessage = data.response || data.conversation_state?.conversation?.slice(-1)[0]?.content || 'No response';
          
          // Save assistant message to database
          const assistantMessageSaved = await saveMessageToDatabase(conversationId, assistantMessage, 'assistant', 'agent');
          if (!assistantMessageSaved) {
            console.error('❌ Failed to save assistant message');
          }
          
          // Check if we have offers to display
          if (data.offers && data.offers.length > 0) {
            appendMessage(assistantMessage, false, false, [], false); // No streaming for offer messages
            displayOfferCards(data.offers);
          } else {
            appendMessage(assistantMessage, false, false, [], false); // No streaming for fallback responses
          }
        } else {
          appendMessage('Désolé, je rencontre des difficultés techniques. Veuillez réessayer dans quelques instants.', false, true, [], false);
        }
      }
    } catch (e) {
      console.error('❌ Error in sendMessage:', e);
      hideLoading();
      appendMessage('Désolé, il y a eu un problème de connexion. Veuillez vérifier votre connexion internet et réessayer.', false, true, [], false);
    } finally {
      console.log('🔄 Resetting send state');
      // Clear the safety timeout
      clearTimeout(safetyTimeout);
      // Re-enable input and button and reset sending flag
      isSending = false;
      chatInput.disabled = false;
      sendButton.disabled = false;
      chatInput.focus();
    }
  }

  // On page load, render conversation history if present or show welcome
  (async function() {
    // Clear memory on page load/refresh to ensure fresh start
    await clearMemory();
    
    await renderConversationHistory();
    
    // Add some initial focus and setup
    setTimeout(() => {
      if (chatInput && !getCurrentConversationId()) {
        chatInput.focus();
      }
    }, 1000);
  })();

  // Handle browser back/forward buttons
  window.addEventListener('popstate', async function() {
    currentConversationId = null; // Reset to force reload from URL
    await renderConversationHistory();
  });

  // Only attach event listeners once
  if (!eventListenersAttached) {
    chatForm.addEventListener('submit', function(e) {
      e.preventDefault();
      if (!isSending) {
        sendMessage();
      } else {
        console.log('🚫 Send blocked - message already being processed');
        // Add visual feedback
        sendButton.style.opacity = '0.5';
        setTimeout(() => {
          sendButton.style.opacity = '1';
        }, 500);
      }
    });

    sendButton.addEventListener('click', function(e) {
      e.preventDefault();
      if (!isSending) {
        sendMessage();
      } else {
        console.log('🚫 Send blocked - message already being processed');
        // Add visual feedback
        sendButton.style.opacity = '0.5';
        setTimeout(() => {
          sendButton.style.opacity = '1';
        }, 500);
      }
    });

    // Add keyboard shortcuts
    chatInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!isSending) {
          sendMessage();
        } else {
          console.log('🚫 Send blocked - message already being processed');
        }
      }
    });
    
    eventListenersAttached = true;
  }

  // New Chat button logic - be more specific
  function setupNewChatButton() {
    const newChatBtns = document.querySelectorAll('.new-chat-btn');
    newChatBtns.forEach(btn => {
      // Remove existing listeners to avoid duplicates
      btn.removeEventListener('click', handleNewChatClick);
      btn.addEventListener('click', handleNewChatClick);
    });
  }

  function handleNewChatClick(e) {
    e.preventDefault();
    createNewConversation();
  }

  // Setup initially
  setupNewChatButton();

  // Also setup after a short delay to ensure DOM is ready
  setTimeout(setupNewChatButton, 100);

  // Also setup when DOM changes (in case sidebar is loaded dynamically)
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.addedNodes.length) {
        setupNewChatButton();
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}); 