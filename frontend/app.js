document.addEventListener('DOMContentLoaded', () => {
  let currentSessionId = null;
  let activeArtifact = null;

  // DOM Elements
  const sessionsList = document.getElementById('sessions-list');
  const chatMessages = document.getElementById('chat-messages');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const providerSelect = document.getElementById('provider-select');
  const providerBadge = document.getElementById('provider-status-badge');
  const btnNewChat = document.getElementById('btn-new-chat');
  const btnShip30 = document.getElementById('btn-ship30-skill');
  const btnDemoArtifact = document.getElementById('btn-demo-artifact');

  // Artifact DOM Elements
  const artifactPanel = document.getElementById('artifact-panel');
  const artifactTitle = document.getElementById('artifact-title');
  const artifactIframe = document.getElementById('artifact-iframe');
  const artifactCodeView = document.getElementById('artifact-code-view');
  const btnCloseArtifact = document.getElementById('btn-close-artifact');
  const tabBtnPreview = document.getElementById('tab-btn-preview');
  const tabBtnCode = document.getElementById('tab-btn-code');

  // Load Initial Data
  fetchConfig();
  fetchSessions();

  // Event Listeners
  btnNewChat.addEventListener('click', startNewChat);

  providerSelect.addEventListener('change', async (e) => {
    const chosen = e.target.value;
    try {
      await fetch('/api/config/provider?provider=' + chosen, { method: 'POST' });
      providerBadge.textContent = `${chosen.toUpperCase()} Active`;
    } catch (err) {
      console.error('Failed to set provider:', err);
    }
  });

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = '';
    appendUserMessage(text);
    showTypingIndicator();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          message: text,
          provider: providerSelect.value
        })
      });
      const data = await res.json();
      removeTypingIndicator();

      if (!currentSessionId) {
        currentSessionId = data.session_id;
        fetchSessions();
      }

      appendAssistantMessage(data.content, data.citations, data.provider_used);

      if (data.artifact) {
        openArtifact(data.artifact);
      }
    } catch (err) {
      removeTypingIndicator();
      appendAssistantMessage('Error connecting to backend API: ' + err.message, [], 'Error');
    }
  });

  btnShip30.addEventListener('click', async () => {
    const topic = prompt('Enter topic for Ship 30 for 30 Atomic Essay:', 'Product-Led Growth Monetization');
    if (!topic) return;

    appendUserMessage(`Generate a Ship 30 for 30 Atomic Essay on: ${topic}`);
    showTypingIndicator();

    try {
      const res = await fetch('/api/skills/ship30', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          topic: topic,
          provider: providerSelect.value
        })
      });
      const data = await res.json();
      removeTypingIndicator();

      if (!currentSessionId) {
        currentSessionId = data.session_id;
        fetchSessions();
      }

      appendAssistantMessage(data.content, data.citations, data.provider_used);

      if (data.artifact) {
        openArtifact(data.artifact);
      }
    } catch (err) {
      removeTypingIndicator();
      appendAssistantMessage('Failed to execute Ship 30 skill: ' + err.message, [], 'Error');
    }
  });

  btnDemoArtifact.addEventListener('click', () => {
    const promptText = "Create an interactive HTML pricing table for a PLG product with Freemium and Enterprise tiers";
    chatInput.value = promptText;
    chatForm.dispatchEvent(new Event('submit'));
  });

  // Quick Prompt Delegates
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('quick-prompt-btn')) {
      const promptText = e.target.getAttribute('data-prompt');
      chatInput.value = promptText;
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  // Artifact Panel Handlers
  btnCloseArtifact.addEventListener('click', () => {
    artifactPanel.classList.add('hidden');
  });

  tabBtnPreview.addEventListener('click', () => {
    tabBtnPreview.classList.add('active');
    tabBtnCode.classList.remove('active');
    artifactIframe.classList.remove('hidden');
    artifactCodeView.classList.add('hidden');
  });

  tabBtnCode.addEventListener('click', () => {
    tabBtnCode.classList.add('active');
    tabBtnPreview.classList.remove('active');
    artifactIframe.classList.add('hidden');
    artifactCodeView.classList.remove('hidden');
  });

  // Helper Functions
  async function fetchConfig() {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      providerSelect.value = data.active_provider;
      providerBadge.textContent = `${data.active_provider.toUpperCase()} Ready`;
    } catch (err) {
      console.warn('Could not fetch config:', err);
    }
  }

  async function fetchSessions() {
    try {
      const res = await fetch('/api/sessions');
      const sessions = await res.json();
      renderSessions(sessions);
    } catch (err) {
      console.warn('Could not fetch sessions:', err);
    }
  }

  function renderSessions(sessions) {
    sessionsList.innerHTML = '';
    sessions.forEach((s) => {
      const li = document.createElement('li');
      li.className = `session-item ${s.id === currentSessionId ? 'active' : ''}`;
      li.innerHTML = `
        <span class="session-title"><i class="fa-regular fa-message"></i> ${escapeHtml(s.title)}</span>
        <button class="btn-delete-session" data-id="${s.id}"><i class="fa-solid fa-trash"></i></button>
      `;

      li.addEventListener('click', (e) => {
        if (e.target.closest('.btn-delete-session')) return;
        loadSession(s.id);
      });

      const delBtn = li.querySelector('.btn-delete-session');
      delBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        await fetch(`/api/sessions/${s.id}`, { method: 'DELETE' });
        if (currentSessionId === s.id) startNewChat();
        else fetchSessions();
      });

      sessionsList.appendChild(li);
    });
  }

  async function loadSession(sessionId) {
    currentSessionId = sessionId;
    fetchSessions();

    try {
      const res = await fetch(`/api/sessions/${sessionId}`);
      const data = await res.json();
      chatMessages.innerHTML = '';

      if (data.messages.length === 0) {
        renderWelcomeCard();
        return;
      }

      data.messages.forEach((msg) => {
        if (msg.role === 'user') {
          appendUserMessage(msg.content);
        } else {
          appendAssistantMessage(msg.content, msg.citations, msg.provider);
        }
      });

      if (data.artifacts && data.artifacts.length > 0) {
        openArtifact(data.artifacts[data.artifacts.length - 1]);
      }
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  }

  function startNewChat() {
    currentSessionId = null;
    chatMessages.innerHTML = '';
    renderWelcomeCard();
    artifactPanel.classList.add('hidden');
    fetchSessions();
  }

  function renderWelcomeCard() {
    chatMessages.innerHTML = `
      <div class="welcome-card">
        <div class="welcome-icon"><i class="fa-solid fa-seedling"></i></div>
        <h2>Welcome to The Lenny Growth Assistant</h2>
        <p>Ask product management and growth questions strictly grounded in transcripts from <strong>Lenny's Podcast</strong>.</p>
        <div class="quick-prompts">
          <button class="quick-prompt-btn" data-prompt="What is Shreyas Doshi's LNO framework for PM time management?">⚡ Shreyas Doshi's LNO Framework</button>
          <button class="quick-prompt-btn" data-prompt="How does Elena Verna define Product Qualified Leads (PQLs) in PLG?">📈 Elena Verna on PLG & PQLs</button>
          <button class="quick-prompt-btn" data-prompt="Explain Brian Balfour's growth loops vs traditional funnels.">🔄 Brian Balfour's Growth Loops</button>
          <button class="quick-prompt-btn" data-prompt="What is Marty Cagan's definition of an Empowered Product Team?">🚀 Marty Cagan on Empowered Teams</button>
        </div>
      </div>
    `;
  }

  function appendUserMessage(text) {
    const welcome = chatMessages.querySelector('.welcome-card');
    if (welcome) welcome.remove();

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble user';
    bubble.textContent = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendAssistantMessage(content, citations, providerName) {
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble assistant';

    let html = `<div class="msg-header"><span><i class="fa-solid fa-robot"></i> Assistant</span><span>${escapeHtml(providerName || 'AI')}</span></div>`;
    html += `<div>${formatMarkdown(content)}</div>`;

    if (citations && citations.length > 0) {
      html += `<div class="citations-box"><div class="citations-title"><i class="fa-solid fa-quote-left"></i> Grounded Evidence Citations</div>`;
      citations.forEach((c) => {
        html += `
          <div class="citation-pill">
            <strong>${escapeHtml(c.title)} (${escapeHtml(c.guest || 'Expert')})</strong>:
            <em>"${escapeHtml(c.snippet)}"</em>
          </div>
        `;
      });
      html += `</div>`;
    }

    bubble.innerHTML = html;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function showTypingIndicator() {
    const ind = document.createElement('div');
    ind.id = 'typing-indicator';
    ind.className = 'message-bubble assistant';
    ind.innerHTML = '<em><i class="fa-solid fa-spinner fa-spin"></i> Searching transcripts and synthesizing answer...</em>';
    chatMessages.appendChild(ind);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function removeTypingIndicator() {
    const ind = document.getElementById('typing-indicator');
    if (ind) ind.remove();
  }

  function openArtifact(art) {
    activeArtifact = art;
    artifactTitle.textContent = art.title || 'Generated Artifact';
    artifactCodeView.querySelector('code').textContent = art.content;

    if (art.type === 'html') {
      artifactIframe.srcdoc = art.content;
    } else {
      artifactIframe.srcdoc = `<html><body style="font-family: sans-serif; padding: 20px; line-height: 1.6; color: #1e293b;"><pre style="white-space: pre-wrap;">${escapeHtml(art.content)}</pre></body></html>`;
    }

    tabBtnPreview.click();
    artifactPanel.classList.remove('hidden');
  }

  function formatMarkdown(text) {
    return escapeHtml(text)
      .replace(/^### (.*$)/gim, '<h3 style="margin-top:12px;margin-bottom:6px;color:#60a5fa;">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 style="margin-top:16px;margin-bottom:8px;color:#3b82f6;">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 style="margin-top:20px;margin-bottom:10px;color:#2563eb;">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
});
