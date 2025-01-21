import { handleClaimSubmission } from "./utilities/handleClaimSubmission.js";
import { initializeChart } from "./utilities/dashboard.js";

// Add the event listener and call the new function
document.getElementById('submit-claim').addEventListener('click', handleClaimSubmission);
initializeChart();