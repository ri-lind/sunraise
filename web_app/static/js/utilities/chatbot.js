/**
 * Initializes the chatbot by calling the backend API with the user's claim.
 * If successful, creates and displays the chatbot panel.
 */
export function initializeChatBot(claim) {
  // Call the backend API to initialize the chatbot
  fetch("/initialize_chatbot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ claim: claim }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(
          `Server error: ${response.status} ${response.statusText}`
        );
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        // Create and show the chatbot slide panel
        createChatbotPanel();
      } else {
        displayErrorInPanel(
          `Initialization failed: ${data.error || "Unknown error"}`
        );
      }
    })
    .catch((error) => {
      console.error("Error initializing chatbot:", error);
      displayErrorInPanel("An error occurred while initializing the chatbot.");
    });
}

/**
 * Creates a sliding chatbot panel dynamically and attaches UI for interactions.
 */
function createChatbotPanel() {
  // Check if the panel already exists
  let panel = document.getElementById("chatbot-panel");
  if (!panel) {
    // Create the sliding panel
    panel = document.createElement("div");
    panel.id = "chatbot-panel";
    panel.style.position = "fixed";
    panel.style.bottom = "0";
    panel.style.right = "-300px";
    panel.style.width = "300px";
    panel.style.height = "50%";
    panel.style.borderLeft = "1px solid #ccc";
    panel.style.borderRadius = "8px";
    panel.style.backgroundColor = "#f9f9f9";
    panel.style.transition = "right 0.3s ease";
    panel.style.display = "flex";
    panel.style.flexDirection = "column";
    panel.innerHTML = `
        <div style="padding: 10px; background-color: #007bff; color: white; display: flex; justify-content: space-between; align-items: center;">
            <h3>Chatbot</h3>
            <button id="close-chatbot" style="color: white; background: none; border: none; font-size: 2rem; cursor: pointer; margin-bottom: 0px;">&times;</button>
        </div>
        <div id="chatbot-content" style="flex: 1; padding: 10px; overflow-y: auto;">
            <p>🤖 Welcome! Ask me anything about your claim.</p>
        </div>
        <div style="padding: 10px; border-top: 1px solid #ddd; display: flex; gap: 10px; height: 80px; align-items: center;">
            <input type="text" id="chatbot-input" placeholder="Type your question..." style="flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 1rem; height: 30%;">
            <button 
                id="chatbot-send" 
                style="
                padding-bottom: 15px; 
                background-color: #007bff; 
                color: white; 
                border: none; 
                border-radius: 55%; 
                cursor: pointer; 
                font-size: 2rem; 
                height: 40px; 
                width: 40px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                line-height: 1;
                margin-bottom: 0;">
            ↑
            </button>

        </div>
        `;

    document.body.appendChild(panel);

    document.getElementById("close-chatbot").addEventListener("click", () => {
      panel.style.right = "-300px";
    });

    attachChatbotListeners();
  }

  panel.style.right = "0";
}

function attachChatbotListeners() {
  document.getElementById("chatbot-send").addEventListener("click", () => {
    const inputField = document.getElementById("chatbot-input");
    const question = inputField.value.trim();

    if (question) {
      sendChatbotMessage(question); // Call the chatbot API
      inputField.value = ""; // Clear the input field
    }
  });

  // Event listener for pressing "Enter" in the input field
  document.getElementById("chatbot-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      document.getElementById("chatbot-send").click();
    }
  });
}

/**
 * Sends the user's question to the backend chatbot API and displays the response.
 */
export function sendChatbotMessage(question) {
  // Call the backend API with the user's question
  fetch("/chatbot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question: question }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(
          `Server error: ${response.status} ${response.statusText}`
        );
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        updateChatUI(question, data.response);
      } else {
        displayErrorInPanel(
          `Failed to get a response: ${data.error || "Unknown error"}`
        );
      }
    })
    .catch((error) => {
      console.error("Error communicating with chatbot:", error);
      displayErrorInPanel(
        "An error occurred while communicating with the chatbot."
      );
    });
}

/**
 * Displays an error message in the chatbot panel.
 */
function displayErrorInPanel(message) {
  const chatbotContent = document.getElementById("chatbot-content");
  const errorMessage = document.createElement("p");
  errorMessage.style.color = "red";
  errorMessage.innerHTML = `<strong>Error:</strong> ${message}`;
  chatbotContent.appendChild(errorMessage);
}

/**
 * Updates the chatbot UI with the user's question and the bot's response.
 */
function updateChatUI(userQuestion, botResponse) {
  const chatbotContent = document.getElementById("chatbot-content");

  // Append the user's question as a styled chat bubble
  const userMessage = document.createElement("div");
  userMessage.classList.add("chat-bubble", "user-message");
  userMessage.innerHTML = `<strong>You:</strong> ${userQuestion}`;
  chatbotContent.appendChild(userMessage);

  // Append the bot's response as a styled chat bubble
  const botMessage = document.createElement("div");
  botMessage.classList.add("chat-bubble", "bot-message");
  botMessage.innerHTML = `<strong>AI:</strong> ${botResponse}`;
  chatbotContent.appendChild(botMessage);

  // Scroll to the bottom of the chatbot panel
  chatbotContent.scrollTop = chatbotContent.scrollHeight;
}
