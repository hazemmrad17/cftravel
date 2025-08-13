// Chat logic with session and conversation state management

// API Configuration - Using Config module
const API_BASE_URL = Config.getApiBaseUrl();

// Global flags to track message states
let isSending = false;         // User is sending a message
let isAITyping = false;        // AI is currently streaming a response
let eventListenersAttached = false;
let typingSoundEnabled = false; // Typing sound effect (disabled by default)
let typingAudioContext = null; // Audio context for typing sounds

document.addEventListener('DOMContentLoaded', function() {
  // Clear memory on page load/refresh to start fresh with error handling
  clearMemory().catch(error => {
    console.warn('⚠️ Failed to clear memory on page load:', error);
    // Continue with page load even if memory clearing fails
  });
  
  // Initialize streaming placeholder effect
  initializeStreamingPlaceholder();
  
  // Cache input and button elements
  let chatInputEl = document.querySelector('#chat-input');
  let sendButtonEl = document.querySelector('#chat-send-btn');
  
  // Function to safely get DOM elements with error handling
  function getChatElements() {
    if (!chatInputEl) chatInputEl = document.querySelector('#chat-input');
    if (!sendButtonEl) sendButtonEl = document.querySelector('#chat-send-btn');
    
    if (!chatInputEl || !sendButtonEl) {
      console.error('Could not find chat input or send button elements');
      return false;
    }
    return true;
  }

    // Update the visual state of the chat interface
  function updateSendStateIndicator() {
    if (!getChatElements()) return;
    
    // Block input and show appropriate state when AI is typing
    if (isAITyping || isSending) {
      // Disable the input field completely
      chatInputEl.disabled = true;
      chatInputEl.readOnly = true;
      chatInputEl.style.pointerEvents = 'none';
      chatInputEl.style.opacity = '0.6';
      chatInputEl.placeholder = 'Veuillez patienter...';
      
      // Add overlay to block any clicks
      if (!document.getElementById('chat-input-overlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'chat-input-overlay';
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.right = '0';
        overlay.style.bottom = '0';
        overlay.style.zIndex = '1000';
        overlay.style.cursor = 'not-allowed';
        overlay.style.backgroundColor = 'transparent';
        chatInputEl.parentNode.style.position = 'relative';
        chatInputEl.parentNode.appendChild(overlay);
      }
      
      // Disable the send button
      if (sendButtonEl) {
        sendButtonEl.disabled = true;
        sendButtonEl.style.pointerEvents = 'none';
        sendButtonEl.style.opacity = '0.6';
      }
      
      // Update button state
      updateButtonIcon();
    } else {
      // Re-enable input when AI is not typing
      chatInputEl.disabled = false;
      chatInputEl.readOnly = false;
      chatInputEl.style.pointerEvents = 'auto';
      chatInputEl.style.opacity = '1';
      // Don't set placeholder here - let the streaming effect handle it
      
      // Re-enable the send button
      if (sendButtonEl) {
        sendButtonEl.disabled = false;
        sendButtonEl.style.pointerEvents = 'auto';
        sendButtonEl.style.opacity = '1';
      }
      
      // Remove overlay if it exists
      const overlay = document.getElementById('chat-input-overlay');
      if (overlay && overlay.parentNode) {
        overlay.parentNode.removeChild(overlay);
      }
      
      // Update button state
      updateButtonIcon();
    }
  }

  // Add custom styling for chat messages
  const style = document.createElement('style');
  style.innerHTML = `
    .loader { 
      border: 3px solid #f3f3f3; 
      border-top: 3px solid #dc2626; 
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
    
    /* Removed typing cursor styles - keeping only clean streaming */
    
    .typing-indicator {
      display: flex;
      align-items: center;
      gap: 4px;
      margin-top: 8px;
      opacity: 0.6;
    }
    
    .typing-dot {
      width: 6px;
      height: 6px;
      background-color: #dc2626;
      border-radius: 50%;
      animation: typing-bounce 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    .typing-dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes typing-bounce {
      0%, 80%, 100% {
        transform: scale(0.8);
        opacity: 0.5;
      }
      40% {
        transform: scale(1);
        opacity: 1;
      }
    }
    
    /* Enhanced typing indicator styles */
    .enhanced-typing {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 12px;
      padding: 8px 12px;
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
      border-radius: 20px;
      border: 1px solid rgba(59, 130, 246, 0.2);
      backdrop-filter: blur(10px);
      animation: typing-glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes typing-glow {
      0% {
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
      }
      100% {
        box-shadow: 0 0 20px rgba(147, 51, 234, 0.4);
      }
    }
    
    .typing-avatar {
      position: relative;
      width: 24px;
      height: 24px;
    }
    
    .avatar-pulse {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #3b82f6, #9333ea);
      border-radius: 50%;
      animation: avatar-pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes avatar-pulse {
      0%, 100% {
        transform: scale(1);
        opacity: 0.8;
      }
      50% {
        transform: scale(1.1);
        opacity: 1;
      }
    }
    
    .typing-dots {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    
    .typing-text {
      font-size: 12px;
      color: #6b7280;
      font-weight: 500;
      animation: text-fade 2s ease-in-out infinite;
    }
    
    @keyframes text-fade {
      0%, 100% {
        opacity: 0.6;
      }
      50% {
        opacity: 1;
      }
    }
    
    /* Smooth streaming animations */
    .message-text {
      transition: all 0.1s ease-out;
    }
    
    .message-text.streaming {
      animation: text-glow 0.2s ease-in-out;
    }
    
    @keyframes text-glow {
      0% {
        opacity: 0.9;
      }
      50% {
        opacity: 1;
      }
      100% {
        opacity: 1;
      }
    }
    

    
    .line-clamp-1 {
      display: -webkit-box;
      -webkit-line-clamp: 1;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .line-clamp-2 {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .line-clamp-3 {
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .backdrop-blur-sm {
      backdrop-filter: blur(4px);
    }
    
    .transform {
      transform: translateZ(0);
    }
    
    .hover\\:-translate-y-1:hover {
      transform: translateY(-0.25rem);
    }
    
    .hover\\:scale-105:hover {
      transform: scale(1.05);
    }
    
    .hover\\:scale-110:hover {
      transform: scale(1.1);
    }
    
    .group:hover .group-hover\\:opacity-30 {
      opacity: 0.3;
    }
    
    .group:hover .group-hover\\:text-blue-600 {
      color: #2563eb;
    }
    
    .dark .group:hover .group-hover\\:text-blue-400 {
      color: #60a5fa;
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
    try {
      // Clear memory first with error handling
      const memoryResult = await clearMemory();
      if (memoryResult && memoryResult.status === 'error') {
        console.warn('⚠️ Memory clearing failed, but continuing with new conversation:', memoryResult.message);
      }
      
      // Clear the chat area
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
      if (chatInputEl) {
        chatInputEl.focus();
      }
    } catch (error) {
      console.error('❌ Error creating new conversation:', error);
      // Still continue with new conversation even if memory clearing fails
      if (chatArea) {
        chatArea.innerHTML = '';
      }
      currentConversationId = null;
      if (chatInputEl) {
        chatInputEl.focus();
      }
    }
  }

  async function clearMemory(conversationId = null) {
    try {
      // Prepare request body with default data if needed
      const body = conversationId ? { conversation_id: conversationId } : { user_id: 1 };
      
      console.log('🧹 Clearing memory with body:', body);
      
      const response = await fetch(`${API_BASE_URL}/chat/memory/clear`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Memory cleared successfully:', data);
        return data;
      } else {
        const errorText = await response.text();
        console.warn('⚠️ Failed to clear memory:', response.status, errorText);
        return { status: 'error', message: `HTTP ${response.status}: ${errorText}` };
      }
    } catch (error) {
      console.warn('⚠️ Error clearing memory:', error);
      return { status: 'error', message: error.message };
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
    
    // Handle "Nouvelle Discussion" button click
    if (e.target.closest('.new-chat-btn')) {
      e.preventDefault();
      createNewConversation();
    }
  });

  // Extract preferences from user message
  function extractPreferencesFromMessage(message) {
    const preferences = {};
    
    // Simple preference extraction based on common patterns
    const messageLower = message.toLowerCase();
    
    // Destination extraction
    const destinations = ['japon', 'japan', 'philippines', 'philippine', 'thaïlande', 'thailand', 'vietnam', 'chine', 'china', 'inde', 'india', 'indonésie', 'indonesia', 'malaisie', 'malaysia', 'singapour', 'singapore', 'cambodge', 'cambodia', 'laos', 'myanmar', 'sri lanka', 'népal', 'nepal', 'bhoutan', 'bhutan', 'mongolie', 'mongolia'];
    
    for (const dest of destinations) {
      if (messageLower.includes(dest)) {
        preferences.destination = dest.charAt(0).toUpperCase() + dest.slice(1);
        break;
      }
    }
    
    // Duration extraction
    if (messageLower.includes('semaine') || messageLower.includes('week')) {
      const weekMatch = messageLower.match(/(\d+)\s*(semaine|week)/);
      if (weekMatch) {
        preferences.duration = `${weekMatch[1]} semaines`;
      }
    } else if (messageLower.includes('jour') || messageLower.includes('day')) {
      const dayMatch = messageLower.match(/(\d+)\s*(jour|day)/);
      if (dayMatch) {
        preferences.duration = `${dayMatch[1]} jours`;
      }
    }
    
    // Budget extraction
    if (messageLower.includes('budget') || messageLower.includes('prix')) {
      if (messageLower.includes('moyen') || messageLower.includes('medium')) {
        preferences.budget = 'Budget moyen';
      } else if (messageLower.includes('élevé') || messageLower.includes('high') || messageLower.includes('luxe')) {
        preferences.budget = 'Budget élevé';
      } else if (messageLower.includes('bas') || messageLower.includes('low') || messageLower.includes('économique')) {
        preferences.budget = 'Budget économique';
      }
    }
    
    // Style extraction
    if (messageLower.includes('culturel') || messageLower.includes('cultural')) {
      preferences.style = 'Culture et découverte';
    } else if (messageLower.includes('aventure') || messageLower.includes('adventure')) {
      preferences.style = 'Aventure';
    } else if (messageLower.includes('détente') || messageLower.includes('relax')) {
      preferences.style = 'Détente et bien-être';
    } else if (messageLower.includes('gastronomie') || messageLower.includes('food')) {
      preferences.style = 'Gastronomie';
    }
    
    return preferences;
  }

  function appendMessage(message, isUser, isError, offers, shouldStream = false) {
    // Remove previous offer cards before rendering new ones
    document.querySelectorAll('.chat-offer-card').forEach(el => el.remove());

    // If offers are present, use the preference confirmation flow
    if (offers && offers.length > 0) {
      // Extract preferences from the current conversation context
      const preferences = extractPreferencesFromMessage(message);
      
             // Display offers directly
       if (window.confirmationFlow && typeof window.confirmationFlow.displayOffers === 'function') {
        // Fallback to direct offer display
        window.confirmationFlow.displayOffers(offers);
      } else {
        // Fallback to simple display if confirmation flow is not available
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
                              <a href="${offer.price_url || '#'}" target="_blank" style="color: #dc2626; text-decoration: none; font-weight: 500;">Voir l'offre</a>
            </div>
          `;
          chatArea.appendChild(offerDiv);
        });
      }
      return; // Do not render the full message if offers are present
    }

    // If no offers, render the message as usual
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex ' + (isUser ? 'justify-end' : 'justify-start') + ' mb-6';
    let html = '';
    
    if (isUser) {
      // Format user message with line breaks
      const formattedUserMessage = message.replace(/\n/g, '<br>');
      html = `
        <div class="bg-chat-user shadow-theme-xs rounded-3xl rounded-tr-lg py-4 px-5 max-w-md" style="background-color: #8B0000 !important;">
          <p class="text-white dark:text-white/90 font-normal">
            ${formattedUserMessage}
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
        // Create empty message element for server streaming with proper initial state
        const streamErrorClass = isError ? 'bg-red-100 dark:bg-red-500 text-red-700 dark:text-white rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl' : 'bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl';
        html = '<div class="' + streamErrorClass + '"><p class="text-gray-800 dark:text-white/90 font-normal message-text streaming" style="opacity: 0.8;"></p></div>';
        msgDiv.innerHTML = html;
        chatArea.appendChild(msgDiv);
        
        // Add a subtle typing indicator
        const textElement = msgDiv.querySelector('.message-text');
        if (textElement) {
          textElement.textContent = 'L\'IA prépare votre réponse...';
          // Don't clear the text after 500ms - let streaming handle it
          // The streaming will clear it when it starts receiving content
        }
        
        // Return the message element for streaming updates
        return msgDiv;
      } else {
        // Show immediately for loaded messages (no streaming)
        const errorClass = isError ? 'bg-red-100 dark:bg-red-500 text-red-700 dark:text-white rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl' : 'bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl';
        // Format message with proper line breaks and bullet points
        let formattedMessage = message;
        
        // Check if the message contains bullet points
        if (message.includes('•')) {
          // Split the message into parts
          const parts = message.split('•');
          const intro = parts[0].trim();
          const bulletPoints = parts.slice(1).map(point => point.trim()).filter(point => point);
          
          // Build HTML with proper structure
          let htmlContent = '';
          if (intro) {
            htmlContent += `<div class="mb-3">${intro}</div>`;
          }
          
          if (bulletPoints.length > 0) {
            htmlContent += '<ul class="list-none space-y-2 mt-3">';
            bulletPoints.forEach(point => {
              htmlContent += `<li class="flex items-start">
                <span class="text-gray-600 dark:text-gray-400 mr-2 mt-1">•</span>
                <span>${point}</span>
              </li>`;
            });
            htmlContent += '</ul>';
          }
          
          html = '<div class="' + errorClass + '">' + htmlContent + '</div>';
        } else {
          // Regular message without bullet points
          formattedMessage = message
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
          html = '<div class="' + errorClass + '"><p class="text-gray-800 dark:text-white/90 font-normal">' + formattedMessage + '</p></div>';
        }
        msgDiv.innerHTML = html;
        chatArea.appendChild(msgDiv);
        // Smooth scroll to bottom
        setTimeout(() => {
          chatArea.scrollTop = chatArea.scrollHeight;
        }, 100);
      }
    }
  }

  function showLoading(message = 'L\'IA rédige...') {
    // Create typing indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'flex justify-start mb-6';
    loadingDiv.id = 'typing-indicator';
    loadingDiv.innerHTML = `
      <div class="bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl">
        <p class="text-gray-800 dark:text-white/90 font-normal">
          ${message} <span class="loader"></span>
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
      <div class="bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg p-6 max-w-6xl">
        <div class="mb-6">
          <div class="flex items-center mb-3">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mr-3">
              <span class="text-white text-sm font-bold">ASIA</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Voyages recommandés</h3>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400">Voici les 3 meilleures offres qui correspondent parfaitement à vos préférences</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          ${offers.map((offer, index) => createOfferCard(offer, index)).join('')}
        </div>
      </div>
    `;
    chatArea.appendChild(offersContainer);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function createOfferCard(offer, index) {
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
              <span class="text-sm text-gray-700 ml-2 font-bold">4.8</span>
            </div>
          </div>
          
          <!-- ASIA.fr Badge -->
          <div class="absolute top-4 left-4">
            <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs px-3 py-1 rounded-full font-bold shadow-xl">
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
            <svg class="w-5 h-5 mr-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span class="line-clamp-1 font-medium">${destinations}</span>
          </div>
          
          <!-- Departure -->
          <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 mb-4">
            <svg class="w-5 h-5 mr-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            <span class="font-medium">Départ: ${offer.departure_city}</span>
          </div>
          
          <!-- Description -->
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2 leading-relaxed">
            ${offer.description}
          </p>
          
          <!-- Highlights -->
          <div class="mb-4">
            <div class="flex flex-wrap gap-1">
              ${offer.highlights.slice(0, 2).map(highlight => `
                <span class="bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 text-blue-800 dark:text-blue-300 text-xs px-2 py-1 rounded-full font-medium shadow-sm">
                  ${highlight.text}
                </span>
              `).join('')}
            </div>
          </div>
          
          <!-- AI Reasoning (if available) -->
          ${offer.ai_reasoning ? `
            <div class="mb-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border-l-4 border-blue-400">
              <div class="flex items-center mb-2">
                <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
                <span class="text-xs font-bold text-blue-800 dark:text-blue-200">Match: ${Math.round(offer.match_score * 100)}%</span>
              </div>
              <p class="text-xs text-blue-700 dark:text-blue-300 leading-relaxed line-clamp-2">${offer.ai_reasoning}</p>
            </div>
          ` : ''}
          
          <!-- Features -->
          <div class="mb-5">
            <div class="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
              <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <span class="font-medium">Inclus: Transport, Hôtel, Guide, Repas</span>
            </div>
          </div>
          
          <!-- Price and Action -->
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
              <button onclick="showOfferDetails('${offer.reference}')" class="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white text-xs px-3 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg font-medium">
                Détails
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function showOfferDetails(offerReference) {
    // Find the offer data from the current offers
    const offerCards = document.querySelectorAll('[data-offer-reference]');
    let offerData = null;
    
    offerCards.forEach(card => {
      if (card.getAttribute('data-offer-reference') === offerReference) {
        offerData = JSON.parse(card.getAttribute('data-offer-data') || '{}');
      }
    });
    
    // Create a modal with detailed offer information
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
          <button onclick="this.closest('.fixed').remove()" class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
            Fermer
          </button>
          ${offerData?.price_url ? `
            <a href="${offerData.price_url}" target="_blank" class="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-6 py-2 rounded-lg transition-all duration-200 font-medium">
              Réserver maintenant
            </a>
          ` : `
            <button onclick="bookOffer('${offerReference}')" class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-4 py-2 rounded-lg transition-all duration-200">
              Réserver
            </button>
          `}
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  function bookOffer(offerReference) {
    // Placeholder for booking functionality
    alert(`Réservation pour l'offre ${offerReference} - Cette fonctionnalité sera bientôt disponible!`);
  }

  function showDetailedProgram(offerReference) {
    // Send a message to get the detailed program
    const message = `Montrez-moi le programme détaillé de l'offre ${offerReference}`;
    
    // Add the message to the chat
    appendMessage(message, true);
    
    // Send the message to get detailed program
    sendMessageWithDetailedProgram(message, offerReference);
  }

  async function sendMessageWithDetailedProgram(message, offerReference) {
    const { chatInput, sendButton } = getChatElements();
    
    try {
      // Disable input and show loading
      chatInput.disabled = true;
      sendButton.disabled = true;
      
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          message: message,
          conversation_id: getCurrentConversationId()
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Add AI response
        appendMessage(data.response, false);
        
        // Display detailed program if available
        if (data.detailed_program) {
          displayDetailedProgram(data.detailed_program);
        }
      } else {
        appendMessage('Désolé, je rencontre des difficultés techniques. Veuillez réessayer.', false, true);
      }
    } catch (error) {
      console.error('Error:', error);
      appendMessage('Désolé, je rencontre des difficultés techniques. Veuillez réessayer.', false, true);
    } finally {
      // Re-enable input
      chatInput.disabled = false;
      sendButton.disabled = false;
      chatInput.focus();
    }
  }

  function displayDetailedProgram(program) {
    const programContainer = document.createElement('div');
    programContainer.className = 'flex justify-start mb-6';
    programContainer.innerHTML = `
      <div class="bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg p-6 max-w-6xl">
        <div class="mb-6">
          <div class="flex items-center mb-4">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mr-4">
              <span class="text-white text-sm font-bold">ASIA</span>
            </div>
            <div>
              <h3 class="text-3xl font-bold text-gray-900 dark:text-white">Programme détaillé</h3>
              <h4 class="text-xl font-semibold text-blue-600 dark:text-blue-400">${program.product_name}</h4>
            </div>
          </div>
          
          <!-- Overview -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 p-4 rounded-xl border border-blue-200 dark:border-blue-700">
              <h5 class="font-bold text-blue-800 dark:text-blue-200 mb-2 flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                Durée
              </h5>
              <p class="text-blue-700 dark:text-blue-300 font-medium">${program.overview.duration} jours</p>
            </div>
            <div class="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 p-4 rounded-xl border border-green-200 dark:border-green-700">
              <h5 class="font-bold text-green-800 dark:text-green-200 mb-2 flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                </svg>
                Groupe
              </h5>
              <p class="text-green-700 dark:text-green-300 font-medium">${program.overview.group_size}</p>
            </div>
            <div class="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 p-4 rounded-xl border border-purple-200 dark:border-purple-700">
              <h5 class="font-bold text-purple-800 dark:text-purple-200 mb-2 flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                Niveau
              </h5>
              <p class="text-purple-700 dark:text-purple-300 font-medium">${program.overview.physical_level}</p>
            </div>
          </div>
          
          <!-- Map Section -->
          <div class="mb-8">
            <h5 class="font-bold text-gray-900 dark:text-white mb-4 flex items-center">
              <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m0 0L9 7"></path>
              </svg>
              Itinéraire sur la carte
            </h5>
            <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-700">
              <div class="flex items-center justify-center h-64 bg-white dark:bg-gray-800 rounded-xl border-2 border-dashed border-blue-300 dark:border-blue-600">
                <div class="text-center">
                  <svg class="w-16 h-16 mx-auto text-blue-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m0 0L9 7"></path>
                  </svg>
                  <p class="text-gray-600 dark:text-gray-400 font-medium">Carte interactive en cours de développement</p>
                  <p class="text-sm text-gray-500 dark:text-gray-500 mt-1">Visualisation de l'itinéraire avec connexions entre destinations</p>
                </div>
              </div>
              <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                ${program.itinerary.slice(0, 3).map((day, index) => `
                  <div class="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                    <div class="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mr-3">
                      <span class="text-white text-xs font-bold">${index + 1}</span>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900 dark:text-white">${day.location}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Jour ${day.day}</p>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
          
          <!-- Highlights -->
          <div class="mb-8">
            <h5 class="font-bold text-gray-900 dark:text-white mb-4 flex items-center">
              <svg class="w-6 h-6 mr-2 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
              </svg>
              Points forts du voyage
            </h5>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              ${program.highlights.map((highlight, index) => `
                <div class="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 p-4 rounded-xl border border-yellow-200 dark:border-yellow-700">
                  <div class="flex items-center">
                    <div class="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mr-3">
                      <span class="text-white text-lg">${highlight.icon}</span>
                    </div>
                    <div>
                      <p class="font-medium text-yellow-800 dark:text-yellow-200">${highlight.text}</p>
                    </div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
          
          <!-- Included/Not Included -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h5 class="font-semibold text-green-800 dark:text-green-200 mb-3">✅ Inclus</h5>
              <ul class="space-y-2">
                ${program.included.map(item => `
                  <li class="flex items-center text-sm text-green-700 dark:text-green-300">
                    <svg class="w-4 h-4 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    ${item}
                  </li>
                `).join('')}
              </ul>
            </div>
            <div>
              <h5 class="font-semibold text-red-800 dark:text-red-200 mb-3">❌ Non inclus</h5>
              <ul class="space-y-2">
                ${program.not_included.map(item => `
                  <li class="flex items-center text-sm text-red-700 dark:text-red-300">
                    <svg class="w-4 h-4 mr-2 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                    ${item}
                  </li>
                `).join('')}
              </ul>
            </div>
          </div>
          
          <!-- Itinerary -->
          <div class="mb-8">
            <h5 class="font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <svg class="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m0 0L9 7"></path>
              </svg>
              Itinéraire détaillé jour par jour
            </h5>
            <div class="space-y-6">
              ${program.itinerary.map((day, index) => `
                <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-700">
                  <div class="flex items-start mb-4">
                    <div class="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mr-4 flex-shrink-0">
                      <span class="text-white text-sm font-bold">${day.day}</span>
                    </div>
                    <div class="flex-1">
                      <h6 class="text-lg font-bold text-gray-900 dark:text-white mb-2">${day.location}</h6>
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Activités:</p>
                          <div class="flex flex-wrap gap-2">
                            ${day.activities.map(activity => `
                              <span class="bg-white dark:bg-gray-800 text-blue-700 dark:text-blue-300 text-xs px-3 py-1 rounded-full border border-blue-200 dark:border-blue-700">
                                ${activity}
                              </span>
                            `).join('')}
                          </div>
                        </div>
                        <div>
                          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Détails:</p>
                          <div class="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                            <div class="flex items-center">
                              <svg class="w-3 h-3 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                              </svg>
                              ${day.accommodation}
                            </div>
                            <div class="flex items-center">
                              <svg class="w-3 h-3 mr-2 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                              </svg>
                              ${day.meals}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
          
          <!-- Practical Info -->
          <div class="mb-6">
            <h5 class="font-semibold text-gray-900 dark:text-white mb-3">ℹ️ Informations pratiques</h5>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="text-sm">
                <span class="font-medium">Meilleure période:</span> ${program.practical_info.best_time}
              </div>
              <div class="text-sm">
                <span class="font-medium">Climat:</span> ${program.practical_info.weather}
              </div>
              <div class="text-sm">
                <span class="font-medium">Devise:</span> ${program.practical_info.currency}
              </div>
              <div class="text-sm">
                <span class="font-medium">Langue:</span> ${program.practical_info.language}
              </div>
            </div>
          </div>
          
          <!-- Pricing -->
          <div class="bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 mb-8">
            <h5 class="font-bold text-gray-900 dark:text-white mb-4 flex items-center">
              <svg class="w-6 h-6 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
              </svg>
              Tarifs et conditions
            </h5>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span class="font-bold text-green-600">Acompte:</span>
                <p class="text-gray-700 dark:text-gray-300 mt-1">${program.pricing.deposit}</p>
              </div>
              <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span class="font-bold text-blue-600">Paiement:</span>
                <p class="text-gray-700 dark:text-gray-300 mt-1">${program.pricing.payment_terms}</p>
              </div>
              <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span class="font-bold text-orange-600">Annulation:</span>
                <p class="text-gray-700 dark:text-gray-300 mt-1">${program.pricing.cancellation}</p>
              </div>
            </div>
          </div>
          
          <!-- Call to Action -->
          <div class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-center">
            <h5 class="text-2xl font-bold text-white mb-4">Prêt à réserver votre voyage ?</h5>
            <p class="text-blue-100 mb-6">Contactez-nous pour obtenir un devis personnalisé et réserver votre place</p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <button onclick="bookOffer('${program.reference}')" class="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 rounded-xl font-bold transition-all duration-300 transform hover:scale-105 shadow-lg">
                Réserver maintenant
              </button>
              <button onclick="showOfferDetails('${program.reference}')" class="bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3 rounded-xl font-bold transition-all duration-300 transform hover:scale-105">
                Plus d'informations
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    chatArea.appendChild(programContainer);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function showWelcomeMessage() {
    // Don't show any welcome message - let the AI respond naturally
    // Just focus on the input field
    setTimeout(() => {
      if (chatInputEl) {
        chatInputEl.focus();
      }
    }, 500);
  }



  function updateStreamingMessage(messageElement, content) {
    // Update the message content with streaming text
    const textElement = messageElement.querySelector('.message-text');
    if (textElement) {
      // Simple and responsive streaming effect
      const currentContent = textElement.textContent || '';
      const newContent = content;
      
      // If content is the same, just scroll
      if (currentContent === newContent) {
      setTimeout(() => {
          chatArea.scrollTo({
            top: chatArea.scrollHeight,
            behavior: 'smooth'
          });
      }, 50);
        return;
      }
      
      // Clear typing indicator if it's still showing
      if (currentContent === 'L\'IA rédige...') {
        textElement.textContent = '';
        textElement.classList.remove('streaming');
        textElement.style.opacity = '1';
      }
      
      // Format content with proper line breaks and bullet points
      const formattedContent = newContent
        .replace(/\n/g, '<br>')
        .replace(/•\s*/g, '<br>• ')
        .replace(/^\s*<br>/, ''); // Remove leading <br> if it exists
      
      // Update with formatted content
      textElement.innerHTML = formattedContent;
      
      // Add subtle visual effect
      textElement.classList.add('streaming');
      setTimeout(() => {
        textElement.classList.remove('streaming');
      }, 150);
      
      // Scroll to bottom
      setTimeout(() => {
        chatArea.scrollTo({
          top: chatArea.scrollHeight,
          behavior: 'smooth'
        });
      }, 10);
    }
  }
  


  async function streamMessageWithEffect(messageElement, fullMessage) {
    // Simulate streaming by displaying the message word by word
    const textElement = messageElement.querySelector('.message-text');
    if (!textElement) return;
    
    // Split the message into words
    const words = fullMessage.split(/\s+/);
    let currentText = '';
    
    // Clear any initial content
    textElement.textContent = '';
    
    // Display words one by one with delays
    for (let i = 0; i < words.length; i++) {
      const word = words[i];
      
      // Add space before word (except first word)
      if (i > 0) {
        currentText += ' ' + word;
      } else {
        currentText += word;
      }
      
      // Update the display
      updateStreamingMessage(messageElement, currentText);
      
      // Add delay between words (shorter for faster response)
      const delay = Math.min(50 + (word.length * 5), 150); // Between 50ms and 150ms
      
      // Extra delay after punctuation for natural flow
      if (word.match(/[.!?:;]$/)) {
        await new Promise(resolve => setTimeout(resolve, delay + 100));
      } else {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    // Finalize the message
    finalizeStreamingMessage(messageElement, currentText);
  }

  function finalizeStreamingMessage(messageElement, content) {
    // Finalize the streaming message
    const textElement = messageElement.querySelector('.message-text');
    if (textElement) {
      // Format content with proper line breaks and bullet points
      const formattedContent = content
        .replace(/\n/g, '<br>')
        .replace(/•\s*/g, '<br>• ')
        .replace(/^\s*<br>/, ''); // Remove leading <br> if it exists
      
      // Set final content without cursor
      textElement.innerHTML = formattedContent;
      textElement.classList.remove('streaming');
      
      // Remove typing indicator
      const typingIndicator = messageElement.querySelector('.typing-indicator');
      if (typingIndicator) {
        typingIndicator.remove();
      }
      
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
      // Just focus on input, no welcome message
      setTimeout(() => {
        if (chatInputEl) {
          chatInputEl.focus();
        }
      }, 500);
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
      // Just focus on input, no welcome message
      setTimeout(() => {
        if (chatInputEl) {
          chatInputEl.focus();
        }
      }, 500);
    }
  }

  // Update sendMessage to remove isSending logic and use cached elements
  async function sendMessage() {
    // Note: isSending is already set to true by handleSendMessage
    // We only need to check isAITyping here
    if (isAITyping) {
      console.log("[DEBUG] AI is already typing, ignoring send request");
      return;
    }
    
    const message = chatInputEl.value.trim();
    console.log("[DEBUG] sendMessage called, message:", message);
    
    // Validate message
    if (!message) {
      console.log("[DEBUG] Empty message, ignoring");
      resetSendState();
      return;
    }
    
    // Check if user is confirming preferences and we have pending offers
    const messageLower = message.toLowerCase();
    const confirmationKeywords = ['oui', 'parfait', 'c\'est bon', 'ok', 'd\'accord', 'confirmer', 'exactement', 'précisément', 'montrer les offres', 'voir les offres', 'c\'est parfait', 'ça me convient', 'parfait', 'montrez-moi', 'je veux voir'];
    const isConfirmation = confirmationKeywords.some(keyword => messageLower.includes(keyword));
    
    if (isConfirmation && window.pendingOffers && window.pendingOffers.length > 0) {
      console.log('✅ User confirmed preferences, displaying pending offers');
      // Display the pending offers
      if (window.confirmationFlow && typeof window.confirmationFlow.displayOffers === 'function') {
        window.confirmationFlow.displayOffers(window.pendingOffers);
      } else {
        // Fallback to the existing displayOfferCards function
        displayOfferCards(window.pendingOffers);
      }
      // Clear pending offers
      window.pendingOffers = null;
    } else if (window.pendingOffers && window.pendingOffers.length > 0) {
      // User is not confirming, so they might want to modify preferences
      // Clear pending offers since they're not confirming
      console.log('🔄 User not confirming, clearing pending offers for potential modification');
      window.pendingOffers = null;
    }
    
    // Clear input now that we have the message
    chatInputEl.value = '';
    
    console.log('🚀 Starting to send message:', message);
    
    // Helper function to reset send state
    function resetSendState() {
      console.log('[DEBUG] resetSendState called - isSending:', isSending, 'isAITyping:', isAITyping);
      isSending = false;
      isAITyping = false; // Also reset AI typing state
      updateSendStateIndicator();
      hideLoading();
      console.log('[DEBUG] resetSendState completed - isSending:', isSending, 'isAITyping:', isAITyping);
    }
    
    // Safety timeout to prevent permanent blocking
    const safetyTimeout = setTimeout(() => {
      console.warn('⚠️ Safety timeout triggered, resetting send state');
      resetSendState();
    }, 60000); // 60 seconds timeout
    
    try {
      // Get or create conversation ID
      let conversationId = getCurrentConversationId();
      if (!conversationId) {
        conversationId = 'conv_' + Date.now();
        currentConversationId = conversationId; // Store it globally
        console.log('[DEBUG] Created new conversation ID:', conversationId);
      } else {
        console.log('[DEBUG] Using existing conversation ID:', conversationId);
      }
    
      // Display user message immediately
      appendMessage(message, true, false, [], false);
      chatInputEl.value = '';
      
      // Show loading indicator
      hideLoading(); // Clear any existing
    showLoading('L\'IA prépare vos offres personnalisées...');
    
      console.log('📡 Attempting streaming request...');
      
      // Set AI typing state
      isAITyping = true;
      updateSendStateIndicator();
      
      // Try streaming first, fallback to regular API
      console.log('[DEBUG] Making API request to:', `${API_BASE_URL}/chat/stream`);
      console.log('[DEBUG] Request body:', JSON.stringify({
        message: message,
        conversation_id: conversationId,
        user_id: "1"
      }));
      
      const streamResponse = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId,
          user_id: "1"
        }),
      });
      
      if (streamResponse.ok) {
        console.log('✅ Streaming response received, processing...');
        
        // Remove loading indicator and create assistant message element for streaming
        hideLoading();
        const assistantMessageElement = appendMessage('', false, false, [], true);
        
        // Get the full response text
        const responseText = await streamResponse.text();
        
        // Extract the actual message and check for offers from the response
        let fullMessage = '';
        let offers = null;
        let needsConfirmation = false;
        let confirmationSummary = null;
        let userPreferences = null;
        
        const lines = responseText.split('\n');
        console.log('📦 Raw streaming response lines:', lines.length);
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              console.log('📨 Parsed streaming data:', data);
              
              if (data.type === 'content' && data.chunk) {
                fullMessage += data.chunk;
              } else if (data.type === 'offers' && data.offers) {
                offers = data.offers;
                console.log('🎁 Offers data found:', offers);
              } else if (data.type === 'confirmation' && data.needs_confirmation) {
                needsConfirmation = data.needs_confirmation;
                confirmationSummary = data.confirmation_summary;
                userPreferences = data.user_preferences;
              } else if (data.offers && !offers) {
                // Direct offers in the data
                offers = data.offers;
                console.log('🎁 Direct offers data found:', offers);
              } else if (data.needs_confirmation && !needsConfirmation) {
                // Direct confirmation data
                needsConfirmation = data.needs_confirmation;
                confirmationSummary = data.confirmation_summary;
                userPreferences = data.user_preferences;
              }
            } catch (e) {
              console.warn('⚠️ Error parsing streaming data:', e);
            }
          }
        }
        
        if (fullMessage) {
          // Use JavaScript streaming effect
          await streamMessageWithEffect(assistantMessageElement, fullMessage);
        } else {
          // Fallback: show the message immediately
          finalizeStreamingMessage(assistantMessageElement, fullMessage);
        }
        
        // Check if we need to display offers or confirmation
        if (offers && offers.length > 0) {
          console.log('🎁 Offers found in streaming response:', offers);
          // Store offers for later display after confirmation
          window.pendingOffers = offers;
          console.log('💾 Offers stored for later display');
        } else if (needsConfirmation) {
          console.log('✅ Confirmation needed in streaming response');
          // Store offers if they exist in context for later display
          if (offers && offers.length > 0) {
            window.pendingOffers = offers;
          }
          // The AI text already contains the confirmation prompt, so we just wait for user input
          console.log('⏳ Waiting for user confirmation or modification');
        } else {
          // Debug: Check if the message contains confirmation keywords
          const messageLower = fullMessage.toLowerCase();
          if (messageLower.includes('voici les offres') || messageLower.includes('offres qui correspondent')) {
            console.log('🔍 Message contains offer keywords but no offers data found');
            console.log('📄 Full message:', fullMessage);
            console.log('📦 All parsed data:', { offers, needsConfirmation, confirmationSummary, userPreferences });
          }
        }
        
        // Reset AI typing state and unblock UI
        isAITyping = false;
        resetSendState();
        chatInputEl && chatInputEl.focus();
        return;
      } else {
        console.log('⚠️ Streaming failed, falling back to regular API');
        isAITyping = true; // Still waiting for AI response
        updateSendStateIndicator();
        
        // Fallback to regular API
        const resp = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
            conversation_id: conversationId,
            user_id: "1"
        }),
      });
        
      hideLoading();
        
      if (resp.ok) {
        const data = await resp.json();
        
        // Get assistant response
        const assistantMessage = data.response || data.conversation_state?.conversation?.slice(-1)[0]?.content || 'No response';
        
        // Assistant message received successfully
        console.log('✅ Assistant message received:', assistantMessage);
        
        // Create message element for streaming effect
        const assistantMessageElement = appendMessage('', false, false, [], true);
        
        // Check if we need confirmation
        if (data.needs_confirmation && data.confirmation_summary) {
          // Use streaming effect for confirmation messages
          await streamMessageWithEffect(assistantMessageElement, assistantMessage);
          // Store offers if they exist for later display
          if (data.offers && data.offers.length > 0) {
            window.pendingOffers = data.offers;
            console.log('💾 Offers stored for later display (fallback API)');
          }
          console.log('⏳ Waiting for user confirmation or modification (fallback API)');
        }
        // Check if we have offers to display
        else if (data.offers && data.offers.length > 0) {
          // Use streaming effect for offer messages
          await streamMessageWithEffect(assistantMessageElement, assistantMessage);
          // Store offers for later display after confirmation
          window.pendingOffers = data.offers;
          console.log('💾 Offers stored for later display (fallback API)');
        } else {
          // Use streaming effect for regular messages
          await streamMessageWithEffect(assistantMessageElement, assistantMessage);
        }
          
          // Check if we have a detailed program to display
          if (data.detailed_program) {
            displayDetailedProgram(data.detailed_program);
          }
      } else {
          appendMessage('Désolé, je rencontre des difficultés techniques. Veuillez réessayer dans quelques instants.', false, true, [], false);
        }
        
        // Reset AI typing state and unblock UI
        isAITyping = false;
        resetSendState();
        chatInputEl && chatInputEl.focus();
      }
    } catch (e) {
      console.error('❌ Error in sendMessage:', e);
      
      // Don't hide loading or reset state on timeout - keep spinner visible
      if (e.name === 'TypeError' && e.message.includes('fetch')) {
        // Network error - keep spinner and show timeout message
        appendMessage('Le serveur prend plus de temps que prévu. Veuillez patienter...', false, true, [], false);
        // Keep isAITyping = true to maintain spinner
        // Don't call resetSendState() to keep input blocked
      } else {
        // Other errors - reset state
        appendMessage('Désolé, il y a eu un problème de connexion. Veuillez vérifier votre connexion internet et réessayer.', false, true, [], false);
        isAITyping = false;
        resetSendState();
      }
    }
  }

  // On page load, render conversation history if present or show welcome
  (async function() {
    // Don't clear memory on page load/refresh - preserve conversation state
    // Memory will only be cleared when explicitly clicking "New Conversation"
    
    await renderConversationHistory();
    
    // Add some initial focus and setup
    setTimeout(() => {
      if (chatInputEl && !getCurrentConversationId()) {
        chatInputEl.focus();
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
    console.log("[DEBUG] Attaching chat event listeners");
    
    // Prevent all form submissions globally
    document.addEventListener('submit', function(e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      return false;
    }, true);
    
    // Unified message sending handler
    const handleSendMessage = (e) => {
      if (e) {
    e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
      }
      
      // Direct check to prevent any possibility of sending while AI is typing
      if (isAITyping || isSending) {
        console.log('Message sending blocked - AI is typing or sending');
        showBlockedNotification();
        return false;
      }
      
      if (!getChatElements()) return;
      
      const message = chatInputEl.value.trim();
      if (message === '') return;
      
      // Set sending state
      isSending = true;
      updateSendStateIndicator();
      
      // Send message (don't clear input yet, let sendMessage handle it)
    sendMessage();
    };
    
    // Form submit handler (Enter key or button click)
    const chatForm = document.querySelector('.chat-form');
    if (chatForm) {
      chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        handleSendMessage(e);
        return false;
      });
    }
    
    function updateButtonIcon() {
      if (!sendButtonEl) return;
    
      if (isAITyping) {
        // Show clock icon when AI is responding
        sendButtonEl.innerHTML = `
          <svg class="w-5 h-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        `;
        sendButtonEl.disabled = true;
        sendButtonEl.style.cursor = 'not-allowed';
        sendButtonEl.title = 'Layla est en train de répondre...';
    
      } else if (isSending) {
        // Show loading spinner when sending
        sendButtonEl.innerHTML = `
          <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        `;
        sendButtonEl.disabled = true;
        sendButtonEl.style.cursor = 'wait';
        sendButtonEl.title = 'Envoi en cours...';
    
      } else {
        // Show send icon when ready
        sendButtonEl.innerHTML = `
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
          </svg>
        `;
        sendButtonEl.disabled = false;
        sendButtonEl.style.cursor = 'pointer';
        sendButtonEl.title = 'Envoyer le message';
      }
    }
    
    
    // Initialize button state
    updateButtonIcon();
    
    // Set up input event listeners if elements exist
    if (getChatElements()) {
      // Send button click handler
      sendButtonEl.addEventListener('click', handleSendMessage);
      
      // Global keydown handler to block all input when AI is typing
      function handleGlobalKeydown(e) {
        // Block all Enter keys in the document when AI is typing or sending
        if ((isAITyping || isSending) && e.key === 'Enter') {
          console.log('[DEBUG] Blocked Enter key - AI is typing or sending');
    e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          return false;
        }
      }

      // Remove any existing listeners to prevent duplicates
      document.removeEventListener('keydown', handleGlobalKeydown, true);
      // Add the listener with capture phase
      document.addEventListener('keydown', handleGlobalKeydown, true);

      // Input field keydown handler for normal operation
      function handleInputKeydown(e) {
        // Always block if AI is typing or sending
        if (isAITyping || isSending) {
          // For Enter key, completely block it
          if (e.key === 'Enter') {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            return false;
          }
        }
        
        // Handle Enter key for normal operation
    if (e.key === 'Enter' && !e.shiftKey) {
          // Prevent default form submission and handle with our function
      e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          
          // Only proceed if not already sending and AI is not typing
          if (!isSending && !isAITyping) {
            handleSendMessage(e);
          }
          return false;
        }
      }
      
      // Set up input event listeners
      chatInputEl.addEventListener('keydown', handleInputKeydown);
      
      // Initialize audio context on first user interaction
      chatInputEl.addEventListener('focus', initAudioContext);
      chatInputEl.addEventListener('input', initAudioContext);
      
      // Block paste and other events when AI is typing
      function blockInputEvents(e) {
        if (isAITyping || isSending) {
          // Block all input events
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          
          // For keydown events, also prevent the default browser behavior
          if (e.type === 'keydown' || e.type === 'keypress' || e.key === 'Enter') {
            e.returnValue = false;
            // Special handling for Enter key
            if (e.key === 'Enter') {
              e.preventDefault();
              // Show notification for blocked input
              showBlockedNotification();
              return false;
            }
          }
          
          // Show notification for blocked input
          showBlockedNotification();
          
          return false;
        }
      }
      
      // Block all input events when AI is typing
      ['paste', 'cut', 'copy', 'keypress', 'keyup', 'input', 'keydown'].forEach(event => {
        chatInputEl.addEventListener(event, blockInputEvents, { capture: true, passive: false });
      });
      
      // Add a global form submit handler to catch all submission attempts
      function handleFormSubmit(e) {
        // Only handle our chat form submissions
        const form = e.target;
        if (!form.matches('form') || !chatInputEl || !form.contains(chatInputEl)) return;
        
        if (isAITyping || isSending) {
          console.log('Form submission blocked - AI is typing or sending');
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          showBlockedNotification();
          return false;
        }
      }
      
      // Add the submit handler with capture phase
      document.addEventListener('submit', handleFormSubmit, true);
      
      // Also handle any programmatic form submissions
      if (typeof HTMLFormElement !== 'undefined') {
        const originalSubmit = HTMLFormElement.prototype.submit;
        HTMLFormElement.prototype.submit = function() {
          if (chatInputEl && this.contains(chatInputEl) && (isAITyping || isSending)) {
            console.log('Programmatic form submission blocked - AI is typing or sending');
            showBlockedNotification();
            return false;
          }
          return originalSubmit.apply(this, arguments);
        };
      }
      
      // Function to show blocked input notification
      function showBlockedNotification() {
        let notification = document.getElementById('typing-notification');
        if (!notification) {
          notification = document.createElement('div');
          notification.id = 'typing-notification';
          notification.textContent = 'Veuillez attendre que Layla ait fini de répondre...';
          notification.style.position = 'fixed';
          notification.style.bottom = '100px';
          notification.style.left = '50%';
          notification.style.transform = 'translateX(-50%)';
          notification.style.backgroundColor = 'rgba(0,0,0,0.8)';
          notification.style.color = 'white';
          notification.style.padding = '10px 20px';
          notification.style.borderRadius = '5px';
          notification.style.zIndex = '10000';
          notification.style.fontSize = '14px';
          notification.style.transition = 'opacity 0.3s';
          document.body.appendChild(notification);
          
          // Remove notification after 2 seconds
          setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
              if (notification && notification.parentNode && document.body.contains(notification)) {
                document.body.removeChild(notification);
              }
            }, 300);
          }, 2000);
        }
      }
    }
    
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

  // Clear memory when page is about to be unloaded (refresh/close)
  window.addEventListener('beforeunload', function() {
    // Use synchronous request to ensure it completes before page unloads
    navigator.sendBeacon(`${API_BASE_URL}/chat/memory/clear`, JSON.stringify({ user_id: 1 }));
  });

  // Function to play typing sound effect
  function playTypingSound() {
    if (!typingSoundEnabled || !typingAudioContext) return;
    
    try {
      // Create a simple beep sound
      const oscillator = typingAudioContext.createOscillator();
      const gainNode = typingAudioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(typingAudioContext.destination);
      
      oscillator.frequency.setValueAtTime(800, typingAudioContext.currentTime);
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.01, typingAudioContext.currentTime); // Very quiet
      gainNode.gain.exponentialRampToValueAtTime(0.001, typingAudioContext.currentTime + 0.1);
      
      oscillator.start(typingAudioContext.currentTime);
      oscillator.stop(typingAudioContext.currentTime + 0.1);
    } catch (e) {
      // Silently fail if audio is not supported
      console.debug('Audio not supported or disabled');
    }
  }

  // Initialize audio context on user interaction
  function initAudioContext() {
    if (!typingAudioContext && typeof AudioContext !== 'undefined') {
      try {
        typingAudioContext = new AudioContext();
        console.log('🎵 Audio context initialized for typing sounds');
      } catch (e) {
        console.debug('Audio context not supported');
      }
    }
  }

  // Streaming placeholder effect for chat input
  function initializeStreamingPlaceholder() {
    const chatInput = document.getElementById('chat-input');
    if (!chatInput) return;

    // Array of trip suggestions with Asia.fr theme
    const placeholders = [
      "Dites-moi où vous voulez partir ou ce que vous cherchez...",
      "Je veux partir au Japon pour 2 semaines en avril...",
      "Cherche des voyages culturels en Thaïlande...",
      "Propose-moi des destinations exotiques en Asie...",
      "Je recherche un voyage romantique au Vietnam...",
      "Aide-moi à planifier un séjour au Cambodge...",
      "Je veux découvrir la Corée du Sud en famille...",
      "Propose des circuits aventure en Indonésie...",
      "Cherche des offres pour la Malaisie en été...",
      "Je veux un voyage gastronomique au Japon..."
    ];

    let currentIndex = 0;
    let typingSpeed = 100; // ms per character
    let deletingSpeed = 50; // ms per character
    let pauseTime = 2000; // ms to pause between placeholders
    let currentInterval = null;
    let isAnimating = false;

    function clearCurrentAnimation() {
      if (currentInterval) {
        clearInterval(currentInterval);
        currentInterval = null;
      }
      isAnimating = false;
    }

    function animatePlaceholder() {
      if (isAnimating) return;
      isAnimating = true;
      
      const targetText = placeholders[currentIndex];
      
      // Type the text
      let charIndex = 0;
      currentInterval = setInterval(() => {
        if (charIndex <= targetText.length) {
          chatInput.placeholder = targetText.substring(0, charIndex) + '|';
          charIndex++;
        } else {
          clearCurrentAnimation();
          
          // Pause at the end
          setTimeout(() => {
            // Delete the text
            let deleteIndex = targetText.length;
            currentInterval = setInterval(() => {
              if (deleteIndex >= 0) {
                chatInput.placeholder = targetText.substring(0, deleteIndex) + '|';
                deleteIndex--;
              } else {
                clearCurrentAnimation();
                
                // Move to next placeholder
                currentIndex = (currentIndex + 1) % placeholders.length;
                
                // Start the next animation
                setTimeout(animatePlaceholder, 500);
              }
            }, deletingSpeed);
          }, pauseTime);
        }
      }, typingSpeed);
    }

    // Start the animation
    setTimeout(animatePlaceholder, 1000);

    // Pause the effect when user focuses on input
    chatInput.addEventListener('focus', () => {
      clearCurrentAnimation();
      chatInput.placeholder = placeholders[0];
    });

    // Resume the effect when user blurs (if input is empty)
    chatInput.addEventListener('blur', () => {
      if (!chatInput.value.trim()) {
        setTimeout(animatePlaceholder, 500);
      }
    });

    // Pause when user starts typing
    chatInput.addEventListener('input', () => {
      if (chatInput.value.trim()) {
        clearCurrentAnimation();
        chatInput.placeholder = placeholders[0];
      }
    });
  }
}); 