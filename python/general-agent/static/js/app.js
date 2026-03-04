// 当前会话ID
let currentSessionId = null;

// 发送消息
async function sendMessage() {
    const input = document.getElementById('input');
    const message = input.value.trim();

    if (!message) return;

    // 显示用户消息
    appendMessage('user', message);

    // 清空输入框
    input.value = '';

    // 禁用发送按钮
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    sendBtn.textContent = '发送中...';

    try {
        // 发送请求
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });

        const data = await response.json();

        // 保存session_id
        if (!currentSessionId) {
            currentSessionId = data.session_id;
        }

        // 显示助手回复
        appendMessage('assistant', data.response);

    } catch (error) {
        console.error('Error:', error);
        appendMessage('assistant', '抱歉，发生了错误。请稍后再试。');
        updateStatus('错误', 'red');
    } finally {
        // 恢复发送按钮
        sendBtn.disabled = false;
        sendBtn.textContent = '发送';
    }
}

// 添加消息到界面
function appendMessage(role, content) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.textContent = content;
    messagesDiv.appendChild(messageDiv);

    // 滚动到底部
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 更新状态
function updateStatus(text, color = '#28a745') {
    const status = document.getElementById('status');
    status.textContent = text;
    status.style.color = color;
}

// 监听Enter键发送
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('input');

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
