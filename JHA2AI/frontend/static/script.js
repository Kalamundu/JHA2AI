
document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const terminal = new Terminal();
    const promptInput = document.getElementById('prompt-input');
    const submitBtn = document.getElementById('submit-btn');
    const messageContainer = document.getElementById('message-container');
    const planList = document.getElementById('plan-list');
    const executePlanBtn = document.getElementById('execute-plan-btn');
    const downloadList = document.getElementById('download-list');

    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = text;
        if (messageContainer) {
            messageContainer.appendChild(messageDiv);
            messageContainer.scrollTop = messageContainer.scrollHeight;
        }
    }

    // Socket connection handling
    socket.on('connect', () => {
        console.log('Connected to server');
        addMessage('Connected to server', 'system');
        if (submitBtn) submitBtn.disabled = false;
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        addMessage('Disconnected from server', 'error');
        if (submitBtn) submitBtn.disabled = true;
    });

    socket.on('error', (error) => {
        console.error('Socket error:', error);
        addMessage('Connection error: ' + error, 'error');
    });

    socket.on('message', (data) => {
        console.log('Received message:', data);
        addMessage(data.text, data.type);
    });

    socket.on('file_update', (data) => {
        const link = document.createElement('a');
        link.href = `/download/${data.filename}`;
        link.textContent = `${data.filename} (${new Date(data.timestamp * 1000).toLocaleString()})`;
        if (downloadList) downloadList.appendChild(link);
    });

    function handleSubmit() {
        const text = promptInput.value.trim();
        if (text) {
            console.log('Sending message:', text);
            socket.emit('user_input', { text });
            promptInput.value = '';
            addMessage(text, 'user');
        }
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', handleSubmit);
    }

    if (promptInput) {
        promptInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
            }
        });
    }

    if (executePlanBtn) {
        executePlanBtn.addEventListener('click', () => {
            const planItems = planList.querySelectorAll('li');
            planItems.forEach((item) => {
                const checkbox = item.querySelector('input[type="checkbox"]');
                if (checkbox?.checked) {
                    const stepText = item.textContent;
                    socket.emit('user_input', { text: stepText });
                }
            });
        });
    }

    // Initialize terminal if element exists
    const terminalElement = document.getElementById('terminal');
    if (terminalElement) {
        terminal.open(terminalElement);
    }
});
