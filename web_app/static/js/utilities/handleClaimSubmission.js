import { handleSentimentGeneration } from "./sentiment_generation.js";
import { updateDashboard } from "./dashboard.js";

export function handleClaimSubmission(){
    const claim = document.getElementById('user-claim').value.trim();
    if (claim) {
        handleSentimentGeneration(claim);
        updateDashboard(claim);
    }
}