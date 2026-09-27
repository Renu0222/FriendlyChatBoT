const input = document.querySelector(".chat-input input");
const sendButton = document.querySelector(".chat-input button");
const messages = document.querySelector(".chat-messages");


function cleanAIResponse(text) {

    // Remove code block markers
    text = text.replace(/```python/gi, "");
    text = text.replace(/```/g, "");

    // Remove bold and italic markdown
    text = text.replace(/\*\*/g, "");
    text = text.replace(/\*/g, "");

    // Remove markdown headings
    text = text.replace(/^#{1,6}\s*/gm, "");

    // Remove horizontal lines
    text = text.replace(/^[-_]{3,}\s*$/gm, "");

    // Clean excessive blank lines
    text = text.replace(/\n{3,}/g, "\n\n");

    return text.trim();
}


function addMessage(text, type) {

    const message = document.createElement("div");

    message.classList.add("message");

    if (type === "user") {

        message.classList.add("user-message");

    } else {

        message.classList.add("bot-message");

        // Clean AI formatting
        text = cleanAIResponse(text);
    }

    // Keep line breaks
    message.style.whiteSpace = "pre-wrap";

    message.textContent = text;

    messages.appendChild(message);

    messages.scrollTop = messages.scrollHeight;

    return message;
}


// Typing animation
function showTyping() {

    const typing = document.createElement("div");

    typing.classList.add(
        "message",
        "bot-message",
        "typing"
    );

    typing.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    messages.appendChild(typing);

    messages.scrollTop = messages.scrollHeight;

    return typing;
}


// Send message
async function sendMessage() {

    const text = input.value.trim();

    if (text === "") {
        return;
    }

    // Show user's message
    addMessage(text, "user");

    // Clear input
    input.value = "";

    // Disable button
    sendButton.disabled = true;

    // Show typing animation
    const typingIndicator = showTyping();


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: text
            })

        });


        const data = await response.json();


        // Remove typing animation
        typingIndicator.remove();


        // Show AI response
        addMessage(data.reply, "bot");


    } catch (error) {

        console.error("Error:", error);

        typingIndicator.remove();

        addMessage(
            "Sorry, something went wrong. Please try again. 😕",
            "bot"
        );
    }


    // Enable button
    sendButton.disabled = false;
}


// Send button
sendButton.addEventListener("click", sendMessage);


// Press Enter to send
input.addEventListener("keypress", function(event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});