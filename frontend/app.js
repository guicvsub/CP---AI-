const conversation = document.querySelector('#conversation');
const emptyState = document.querySelector('#empty-state');
const form = document.querySelector('#chat-form');
const textarea = document.querySelector('#message');
const sendButton = document.querySelector('#send');
const statusBox = document.querySelector('#status');
const modelSelect = document.querySelector('#model');
let messages = [];

function setStatus(text = '', kind = '') {
  statusBox.textContent = text;
  statusBox.className = `status ${kind}`;
}

function addMessage(role, content) {
  emptyState?.remove();
  const row = document.createElement('div');
  row.className = `message ${role}`;
  const avatar = role === 'assistant' ? '<div class="avatar">✦</div>' : '';
  row.innerHTML = `${avatar}<div class="bubble"></div>`;
  row.querySelector('.bubble').textContent = content;
  conversation.appendChild(row);
  conversation.scrollTop = conversation.scrollHeight;
}

async function loadConfig() {
  try {
    const response = await fetch('/api/config');
    const config = await response.json();
    Object.entries(config.models).forEach(([name, value]) => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = `${name.replaceAll('_', ' ')} · ${value}`;
      option.selected = value === config.default_model;
      modelSelect.appendChild(option);
    });
  } catch {
    setStatus('Não foi possível carregar a configuração.', 'error');
  }
}

async function sendMessage(content) {
  messages.push({ role: 'user', content });
  addMessage('user', content);
  sendButton.disabled = true;
  textarea.disabled = true;
  setStatus('O modelo está pensando…', 'loading');
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: modelSelect.value, messages }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'Não foi possível obter uma resposta.');
    messages.push({ role: 'assistant', content: payload.answer });
    addMessage('assistant', payload.answer);
    setStatus(`Resposta recebida · ${payload.sent_messages} mensagens enviadas ao modelo`);
  } catch (error) {
    // Retira a mensagem do histórico local para permitir reenviar após uma falha.
    messages.pop();
    setStatus(error.message, 'error');
  } finally {
    sendButton.disabled = false;
    textarea.disabled = false;
    textarea.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const content = textarea.value.trim();
  if (!content || sendButton.disabled) return;
  textarea.value = '';
  textarea.style.height = 'auto';
  sendMessage(content);
});

textarea.addEventListener('input', () => {
  textarea.style.height = 'auto';
  textarea.style.height = `${Math.min(textarea.scrollHeight, 130)}px`;
});

textarea.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelector('#new-session').addEventListener('click', () => {
  messages = [];
  conversation.innerHTML = '<div id="empty-state" class="empty-state"><div class="empty-icon">✦</div><h2>Comece uma conversa</h2><p>Envie uma mensagem para receber uma resposta do modelo selecionado.</p></div>';
  setStatus('Nova conversa iniciada.');
  textarea.focus();
});

loadConfig();
