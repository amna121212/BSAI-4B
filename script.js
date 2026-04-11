async function sendMessage(customMessage = null) {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    const message = customMessage || input.value.trim();
    if (message === "") return;

    const userDiv = document.createElement("div");
    userDiv.className = "user-message";
    userDiv.textContent = message;
    chatBox.appendChild(userDiv);

    input.value = "";

    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    });

    const data = await response.json();

    const botDiv = document.createElement("div");
    botDiv.className = "bot-message";
    botDiv.innerHTML = data.response;
    chatBox.appendChild(botDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendQuickMessage(message) {
    sendMessage(message);
}

document.getElementById("user-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});