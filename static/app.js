
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatArea = document.getElementById("chatArea");
const sendButton = document.getElementById("sendButton");
const welcomeScreen = document.getElementById("welcomeScreen");

// Display a chat message safely
function addMessage(text, sender) {

    const message = document.createElement("div");
    message.className = `message ${sender}-message`;

    const avatar = document.createElement("div");
    avatar.className = `avatar ${
        sender === "user" ? "user-avatar" : "bot-avatar"
    }`;

    avatar.textContent = sender === "user" ? "You" : "AI";

    const content = document.createElement("div");
    content.className = "message-content";

    const name = document.createElement("div");
    name.className = "message-name";
    name.textContent = sender === "user"
        ? "You"
        : "The Last Signal Assistant";

    const messageText = document.createElement("div");
    messageText.className = "message-text";
    messageText.textContent = text;

    content.appendChild(name);
    content.appendChild(messageText);

    message.appendChild(avatar);
    message.appendChild(content);

    chatArea.appendChild(message);

    chatArea.scrollTop = chatArea.scrollHeight;
}


// Show loading indicator
function showTyping() {

    const typing = document.createElement("div");
    typing.id = "typingIndicator";
    typing.className = "message";

    typing.innerHTML = `
        <div class="avatar bot-avatar">AI</div>
        <div class="message-content">
            <div class="message-name">
                The Last Signal Assistant
            </div>
            <div class="typing">Searching the knowledge base...</div>
        </div>
    `;

    chatArea.appendChild(typing);
    chatArea.scrollTop = chatArea.scrollHeight;
}


// Remove loading indicator
function removeTyping() {
    const typing = document.getElementById("typingIndicator");

    if (typing) {
        typing.remove();
    }
}


// Send question to Flask backend
async function sendMessage(question) {

    if (!question.trim() || sendButton.disabled) return;

    welcomeScreen.style.display = "none";

    addMessage(question, "user");

    messageInput.value = "";
    messageInput.style.height = "auto";

    sendButton.disabled = true;
    showTyping();

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: question
            })
        });

        const data = await response.json();

        removeTyping();

        if (!response.ok) {
            throw new Error(data.error || "Request failed");
        }

        addMessage(data.answer, "assistant");

    } catch (error) {

        removeTyping();

        addMessage(
            "Sorry, something went wrong: " + error.message,
            "assistant"
        );

    } finally {

        sendButton.disabled = false;
        messageInput.focus();
    }
}


// Form submission
chatForm.addEventListener("submit", function(event) {

    event.preventDefault();

    sendMessage(messageInput.value);

});


// Suggested questions
document.querySelectorAll(".suggestion").forEach(button => {

    button.addEventListener("click", function() {

        const question = this.dataset.question;

        sendMessage(question);

    });

});


// Enter to send, Shift + Enter for new line
messageInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();
        chatForm.requestSubmit();

    }

});


// Automatically expand textarea
messageInput.addEventListener("input", function() {

    this.style.height = "auto";

    this.style.height =
        Math.min(this.scrollHeight, 140) + "px";

});
