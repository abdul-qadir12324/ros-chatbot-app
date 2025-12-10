// ros-chatbot-app/static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Function to add a message to the chat
    function addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        const messageBubble = document.createElement('div');
        messageBubble.classList.add('message-bubble');
        messageBubble.textContent = message;
        messageDiv.appendChild(messageBubble);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    }

    // Function to send a message to the backend
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        addMessage('user', message);
        userInput.value = ''; // Clear input

        // Show a "typing" indicator or similar
        const botThinkingMessage = document.createElement('div');
        botThinkingMessage.classList.add('message', 'bot');
        botThinkingMessage.innerHTML = '<div class="message-bubble">Typing...</div>';
        chatMessages.appendChild(botThinkingMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });

            const data = await response.json();
            
            // Remove typing indicator
            chatMessages.removeChild(botThinkingMessage);

            addMessage('bot', data.response);
        } catch (error) {
            console.error('Error sending message:', error);
            chatMessages.removeChild(botThinkingMessage);
            addMessage('bot', 'Sorry, something went wrong. Please try again.');
        }
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Initial bot message
    addMessage('bot', 'Hi there! Ask me anything about the Physical AI & Humanoid Robotics Textbook.');
});
