document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const currentSessionInput = document.getElementById('current-session-id');
    const historyList = document.getElementById('history-list');
    const newChatBtn = document.getElementById('new-chat-btn');

    function appendMessage(text, senderClass) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${senderClass}`;
        msgDiv.innerHTML = marked.parse(text);
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addSessionToSidebar(sessionId, summary) {
        document.querySelectorAll('.history-item').forEach(item => {
            item.classList.remove('active');
        });

        const btn = document.createElement('button');
        btn.className = 'history-item active';
        btn.dataset.sessionId = sessionId;
        btn.textContent = summary || '新對話';
        
        historyList.insertBefore(btn, historyList.firstChild);
    }

    newChatBtn.addEventListener('click', () => {
        currentSessionInput.value = '';
        chatBox.innerHTML = '<div class="message ai-msg welcome-msg">你好！我是涵涵，今天想跟我分享什麼呢？</div>';
        
        document.querySelectorAll('.history-item').forEach(item => {
            item.classList.remove('active');
        });

        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.placeholder = "跟涵涵說點什麼...";
    });

    historyList.addEventListener('click', async (e) => {
        const btn = e.target.closest('.history-item');
        if (!btn) return;

        const sessionId = btn.dataset.sessionId;
        if (currentSessionInput.value === sessionId) return;

        document.querySelectorAll('.history-item').forEach(item => item.classList.remove('active'));
        btn.classList.add('active');
        currentSessionInput.value = sessionId;

        chatBox.innerHTML = '<div class="message ai-msg welcome-msg">載入歷史紀錄中...</div>';
        messageInput.disabled = true;
        sendBtn.disabled = true;

        try {
            const url = new URL(API_ENDPOINTS.history, window.location.origin);
            url.searchParams.append('session_id', sessionId);

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();

            if (data.status === 'SUCCESS') {
                chatBox.innerHTML = ''; 
                
                if (data.messages.length === 0) {
                    chatBox.innerHTML = '<div class="message ai-msg welcome-msg">這是空的對話。</div>';
                } else {
                    data.messages.forEach(msg => {
                        const senderClass = (msg.sender === 'user') ? 'user-msg' : 'ai-msg';
                        appendMessage(msg.content, senderClass);
                    });
                }

                messageInput.disabled = false;
                sendBtn.disabled = false;
                messageInput.placeholder = "跟涵涵說點什麼...";
                messageInput.focus();
                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                chatBox.innerHTML = `<div class="message sos-msg">❌ 載入失敗：${data.message}</div>`;
            }
        } catch (error) {
            console.error('Error fetching history:', error);
            chatBox.innerHTML = '<div class="message sos-msg">❌ 連線發生錯誤，無法載入歷史紀錄。</div>';
        }
    });

    async function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return; 

        appendMessage(`${text}`, 'user-msg');
        messageInput.value = '';

        try {
            const payload = {
                message: text,
                session_id: currentSessionInput.value 
            };

            const response = await fetch(API_ENDPOINTS.send, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(payload) 
            });

            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                const data = await response.json();
                if (data.status === 'SOS_TRIGGERED') {
                    appendMessage(`⚠️ 系統提示：${data.message}`, 'sos-msg');
                    appendMessage(`💡 建議行動：${data.action}`, 'sos-msg');
                    messageInput.disabled = true;
                    sendBtn.disabled = true;
                    messageInput.placeholder = "請聯繫上述專業機構尋求協助...";
                } else {
                    appendMessage(`❌ 發生錯誤：${data.message}`, 'sos-msg');
                }
                return; 
            }
            
            const newSessionId = response.headers.get('X-Session-ID');
            const newSessionSummary = decodeURIComponent(response.headers.get('X-Session-Summary') || '');
            
            if (!currentSessionInput.value && newSessionId) {
                currentSessionInput.value = newSessionId;
                addSessionToSidebar(newSessionId, newSessionSummary);
            }

            const msgDiv = document.createElement('div');
            msgDiv.className = `message ai-msg`;
            chatBox.appendChild(msgDiv);
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let aiFullText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break; 
                
                aiFullText += decoder.decode(value, {stream: true});
                msgDiv.innerHTML = marked.parse(aiFullText);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

        } catch (error) {
            console.error('Error:', error);
            appendMessage('❌ 連線發生錯誤，請檢查網路或稍後再試', 'sos-msg');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            if (e.shiftKey) {
                return; 
            }
            e.preventDefault(); 
            sendMessage();
        } 
    });
});