import { handleClaimSubmission } from "./utilities/handleClaimSubmission.js";
import { initializeChart } from "./utilities/dashboard.js";
import { initializeChatBot } from "./utilities/chatbot.js";

let isChatBotOpen = false;

document.getElementById('submit-claim').addEventListener('click', handleClaimSubmission);
initializeChart();

document.getElementById("chatbot-toggle").addEventListener("click", () => {
  const button = document.getElementById("chatbot-toggle");
  let panel = document.getElementById("chatbot-panel");

  if (!isChatBotOpen) {
    if (!panel) {
      const claim = document.getElementById('user-claim')?.value.trim() || '';
      initializeChatBot(claim);
      panel = document.getElementById("chatbot-panel");
    }
		
    panel.style.right = "0";
    button.style.right = "320px"; 
  } else {
    panel.style.right = "-300px";
    button.style.right = "20px"; 
  }

  isChatBotOpen = !isChatBotOpen;
});