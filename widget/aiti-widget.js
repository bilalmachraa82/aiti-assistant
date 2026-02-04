/**
 * AITI Assistant Widget
 * Embeddable chat widget for websites
 * 
 * Usage:
 * <script src="https://your-domain.com/widget/aiti-widget.js"></script>
 * <script>
 *   AITIWidget.init({
 *     apiUrl: 'https://api.your-domain.com',
 *     apiKey: 'your-api-key',
 *     primaryColor: '#0066cc',
 *     welcomeMessage: 'Olá! Como posso ajudar?',
 *     position: 'bottom-right'
 *   });
 * </script>
 */

(function() {
    'use strict';

    // Default configuration
    const defaultConfig = {
        apiUrl: window.location.origin,
        apiKey: null,
        primaryColor: '#0066cc',
        textColor: '#ffffff',
        welcomeMessage: 'Olá! 👋 Como posso ajudar?',
        placeholder: 'Escreva a sua pergunta...',
        position: 'bottom-right', // bottom-right, bottom-left
        title: 'Assistente Virtual',
        subtitle: 'Estamos aqui para ajudar',
        showPoweredBy: true
    };

    let config = { ...defaultConfig };
    let isOpen = false;
    let conversationId = null;
    let messages = [];

    // Initialize widget
    function init(userConfig) {
        config = { ...defaultConfig, ...userConfig };
        injectStyles();
        createWidget();
        attachEventListeners();
    }

    // Inject CSS styles
    function injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .aiti-widget-container {
                position: fixed;
                ${config.position === 'bottom-left' ? 'left: 20px;' : 'right: 20px;'}
                bottom: 20px;
                z-index: 999999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            }

            .aiti-widget-button {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: ${config.primaryColor};
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .aiti-widget-button:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 20px rgba(0,0,0,0.2);
            }

            .aiti-widget-button svg {
                width: 28px;
                height: 28px;
                fill: ${config.textColor};
            }

            .aiti-chat-window {
                position: absolute;
                ${config.position === 'bottom-left' ? 'left: 0;' : 'right: 0;'}
                bottom: 70px;
                width: 380px;
                height: 520px;
                background: #fff;
                border-radius: 16px;
                box-shadow: 0 5px 40px rgba(0,0,0,0.16);
                display: none;
                flex-direction: column;
                overflow: hidden;
            }

            .aiti-chat-window.open {
                display: flex;
                animation: aiti-slide-up 0.3s ease;
            }

            @keyframes aiti-slide-up {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .aiti-chat-header {
                background: ${config.primaryColor};
                color: ${config.textColor};
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .aiti-chat-header-avatar {
                width: 45px;
                height: 45px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .aiti-chat-header-avatar svg {
                width: 24px;
                height: 24px;
                fill: ${config.textColor};
            }

            .aiti-chat-header-info {
                flex: 1;
            }

            .aiti-chat-header-title {
                font-size: 16px;
                font-weight: 600;
                margin: 0;
            }

            .aiti-chat-header-subtitle {
                font-size: 12px;
                opacity: 0.9;
                margin: 2px 0 0;
            }

            .aiti-chat-close {
                background: none;
                border: none;
                color: ${config.textColor};
                cursor: pointer;
                padding: 8px;
                opacity: 0.8;
            }

            .aiti-chat-close:hover {
                opacity: 1;
            }

            .aiti-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .aiti-message {
                max-width: 80%;
                padding: 12px 16px;
                border-radius: 16px;
                font-size: 14px;
                line-height: 1.4;
                animation: aiti-message-in 0.2s ease;
            }

            @keyframes aiti-message-in {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }

            .aiti-message-bot {
                background: #f0f2f5;
                color: #1a1a1a;
                align-self: flex-start;
                border-bottom-left-radius: 4px;
            }

            .aiti-message-user {
                background: ${config.primaryColor};
                color: ${config.textColor};
                align-self: flex-end;
                border-bottom-right-radius: 4px;
            }

            .aiti-message-typing {
                background: #f0f2f5;
                align-self: flex-start;
                padding: 16px 20px;
            }

            .aiti-typing-dots {
                display: flex;
                gap: 4px;
            }

            .aiti-typing-dots span {
                width: 8px;
                height: 8px;
                background: #999;
                border-radius: 50%;
                animation: aiti-typing 1.4s infinite;
            }

            .aiti-typing-dots span:nth-child(2) { animation-delay: 0.2s; }
            .aiti-typing-dots span:nth-child(3) { animation-delay: 0.4s; }

            @keyframes aiti-typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-8px); }
            }

            .aiti-chat-input-area {
                padding: 16px;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
            }

            .aiti-chat-input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #e0e0e0;
                border-radius: 24px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.2s;
            }

            .aiti-chat-input:focus {
                border-color: ${config.primaryColor};
            }

            .aiti-chat-send {
                width: 44px;
                height: 44px;
                background: ${config.primaryColor};
                border: none;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
            }

            .aiti-chat-send:hover {
                background: ${adjustColor(config.primaryColor, -20)};
            }

            .aiti-chat-send:disabled {
                background: #ccc;
                cursor: not-allowed;
            }

            .aiti-chat-send svg {
                width: 20px;
                height: 20px;
                fill: ${config.textColor};
            }

            .aiti-powered-by {
                text-align: center;
                padding: 8px;
                font-size: 11px;
                color: #999;
            }

            .aiti-powered-by a {
                color: #666;
                text-decoration: none;
            }

            .aiti-sources {
                margin-top: 8px;
                padding-top: 8px;
                border-top: 1px solid rgba(0,0,0,0.1);
                font-size: 11px;
                color: #666;
            }

            @media (max-width: 420px) {
                .aiti-chat-window {
                    width: calc(100vw - 40px);
                    height: 70vh;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Adjust color brightness
    function adjustColor(color, amount) {
        const clamp = (num) => Math.min(255, Math.max(0, num));
        const hex = color.replace('#', '');
        const r = clamp(parseInt(hex.slice(0, 2), 16) + amount);
        const g = clamp(parseInt(hex.slice(2, 4), 16) + amount);
        const b = clamp(parseInt(hex.slice(4, 6), 16) + amount);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    // Create widget HTML
    function createWidget() {
        const container = document.createElement('div');
        container.className = 'aiti-widget-container';
        container.innerHTML = `
            <div class="aiti-chat-window" id="aiti-chat">
                <div class="aiti-chat-header">
                    <div class="aiti-chat-header-avatar">
                        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                    </div>
                    <div class="aiti-chat-header-info">
                        <p class="aiti-chat-header-title">${config.title}</p>
                        <p class="aiti-chat-header-subtitle">${config.subtitle}</p>
                    </div>
                    <button class="aiti-chat-close" id="aiti-close">✕</button>
                </div>
                <div class="aiti-chat-messages" id="aiti-messages">
                    <div class="aiti-message aiti-message-bot">${config.welcomeMessage}</div>
                </div>
                <div class="aiti-chat-input-area">
                    <input type="text" class="aiti-chat-input" id="aiti-input" placeholder="${config.placeholder}">
                    <button class="aiti-chat-send" id="aiti-send">
                        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                    </button>
                </div>
                ${config.showPoweredBy ? '<div class="aiti-powered-by">Powered by <a href="https://aiparati.pt" target="_blank">AiParaTi</a></div>' : ''}
            </div>
            <button class="aiti-widget-button" id="aiti-toggle">
                <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>
            </button>
        `;
        document.body.appendChild(container);
    }

    // Attach event listeners
    function attachEventListeners() {
        const toggle = document.getElementById('aiti-toggle');
        const close = document.getElementById('aiti-close');
        const input = document.getElementById('aiti-input');
        const send = document.getElementById('aiti-send');
        const chat = document.getElementById('aiti-chat');

        toggle.addEventListener('click', () => {
            isOpen = !isOpen;
            chat.classList.toggle('open', isOpen);
            if (isOpen) input.focus();
        });

        close.addEventListener('click', () => {
            isOpen = false;
            chat.classList.remove('open');
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                sendMessage(input.value.trim());
                input.value = '';
            }
        });

        send.addEventListener('click', () => {
            if (input.value.trim()) {
                sendMessage(input.value.trim());
                input.value = '';
            }
        });
    }

    // Add message to chat
    function addMessage(text, isBot, sources = null) {
        const container = document.getElementById('aiti-messages');
        const msg = document.createElement('div');
        msg.className = `aiti-message ${isBot ? 'aiti-message-bot' : 'aiti-message-user'}`;
        
        let html = text;
        if (sources && sources.length > 0) {
            html += `<div class="aiti-sources">📚 Fontes: ${sources.map(s => s.file).join(', ')}</div>`;
        }
        msg.innerHTML = html;
        
        container.appendChild(msg);
        container.scrollTop = container.scrollHeight;
    }

    // Show typing indicator
    function showTyping() {
        const container = document.getElementById('aiti-messages');
        const typing = document.createElement('div');
        typing.className = 'aiti-message aiti-message-typing';
        typing.id = 'aiti-typing';
        typing.innerHTML = '<div class="aiti-typing-dots"><span></span><span></span><span></span></div>';
        container.appendChild(typing);
        container.scrollTop = container.scrollHeight;
    }

    // Hide typing indicator
    function hideTyping() {
        const typing = document.getElementById('aiti-typing');
        if (typing) typing.remove();
    }

    // Send message to API
    async function sendMessage(text) {
        // Add user message
        addMessage(text, false);
        messages.push({ role: 'user', content: text });

        // Show typing
        showTyping();
        document.getElementById('aiti-send').disabled = true;

        try {
            const response = await fetch(`${config.apiUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(config.apiKey && { 'Authorization': `Bearer ${config.apiKey}` })
                },
                body: JSON.stringify({
                    query: text,
                    conversation_id: conversationId,
                    conversation_history: messages.slice(-10)
                })
            });

            const data = await response.json();

            hideTyping();
            
            if (response.ok) {
                conversationId = data.conversation_id;
                addMessage(data.response, true, data.sources);
                messages.push({ role: 'assistant', content: data.response });
            } else {
                addMessage('Desculpe, ocorreu um erro. Tente novamente.', true);
            }
        } catch (error) {
            hideTyping();
            addMessage('Não foi possível conectar ao servidor. Tente novamente.', true);
            console.error('AITI Widget Error:', error);
        }

        document.getElementById('aiti-send').disabled = false;
        document.getElementById('aiti-input').focus();
    }

    // Expose global API
    window.AITIWidget = {
        init: init,
        open: () => {
            isOpen = true;
            document.getElementById('aiti-chat').classList.add('open');
        },
        close: () => {
            isOpen = false;
            document.getElementById('aiti-chat').classList.remove('open');
        },
        sendMessage: sendMessage
    };
})();
