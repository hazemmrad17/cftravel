console.log('chat.js loaded');

document.addEventListener('DOMContentLoaded', function () {
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
      const row = btn.closest('.group');
      const titleLink = row.querySelector('a');
      const oldTitle = titleLink.textContent.trim();
      const convId = row.querySelector('[data-conversation-id]').getAttribute('data-conversation-id');
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
          .then(r => r.json())
          .then(data => {
            if (data.success) {
              titleLink.textContent = newTitle;
            }
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
      if (!confirm('Delete this conversation?')) return;
      const btn = e.target.closest('[data-action="delete"]');
      const row = btn.closest('.group');
      const convId = row.querySelector('[data-conversation-id]').getAttribute('data-conversation-id');
      fetch(`/chat/conversation/${convId}/delete`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          row.parentElement.removeChild(row);
        }
      });
      return;
    }
  });

  // Chat logic
  const chatForm = document.getElementById('chat-form');
  const chatInput = chatForm ? chatForm.querySelector('input, textarea') : null;
  const chatMessages = document.querySelector('.chat-messages');

  // Typing indicator element
  let typingIndicator = null;

  function showTypingIndicator() {
    if (!typingIndicator) {
      typingIndicator = document.createElement('div');
      typingIndicator.className = 'ai-typing-indicator text-gray-400 italic mb-2';
      typingIndicator.textContent = 'CFtravel is typing...';
      chatMessages.appendChild(typingIndicator);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  function hideTypingIndicator() {
    if (typingIndicator) {
      typingIndicator.remove();
      typingIndicator = null;
    }
  }

  function typeWriterEffect(element, text, speed = 18, callback) {
    let i = 0;
    function type() {
      if (i < text.length) {
        element.innerHTML += text.charAt(i);
        i++;
        chatMessages.scrollTop = chatMessages.scrollHeight;
        setTimeout(type, speed);
      } else if (callback) {
        callback();
      }
    }
    type();
  }

  if (chatForm && chatInput && chatMessages) {
    chatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      // Show user message immediately
      const userMsgDiv = document.createElement('div');
      userMsgDiv.className = 'mb-4 flex justify-end';
      userMsgDiv.innerHTML = `<div class="bg-chat-user shadow-theme-xs bg-primary-100 dark:bg-primary-500 rounded-3xl rounded-tr-lg py-4 px-5 max-w-md ml-auto"><p class="text-gray-800 dark:text-white/90 font-normal">${message}</p></div>`;
      chatMessages.appendChild(userMsgDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      chatInput.value = '';
      chatInput.disabled = true;

      // Show typing indicator
      showTypingIndicator();

      // Send to backend (adjust URL and payload as needed)
      const userId = chatForm.dataset.userId || 1;
      fetch(chatForm.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message,
          user_id: parseInt(userId)
        }) // Adjust as needed for your backend
      })
      .then(res => res.json())
      .then(data => {
        hideTypingIndicator();
        // Render AI response with typing effect
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'mb-4 flex justify-start';
        aiMsgDiv.innerHTML = `<div class="bg-chat-ai bg-white dark:bg-white/5 shadow-theme-xs rounded-3xl rounded-bl-lg py-4 px-5 max-w-3xl"><p class="text-gray-800 dark:text-white/90 text-base leading-7"></p></div>`;
        chatMessages.appendChild(aiMsgDiv);
        const aiMsgP = aiMsgDiv.querySelector('p');
        // Only use typeWriterEffect, do NOT set aiMsgP.innerHTML directly
        const aiText = data.response || '';
        console.log('Calling typeWriterEffect with:', aiText);
        typeWriterEffect(aiMsgP, aiText, 18, function () {
          chatInput.disabled = false;
          chatInput.focus();
        });
      })
      .catch(() => {
        hideTypingIndicator();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'mb-4 flex justify-start';
        errorDiv.innerHTML = `<div class="bg-red-100 text-red-700 rounded-3xl py-4 px-5 max-w-3xl">Sorry, there was an error. Please try again.</div>`;
        chatMessages.appendChild(errorDiv);
        chatInput.disabled = false;
        chatInput.focus();
      });
    });
  }
}); 