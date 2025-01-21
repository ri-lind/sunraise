import { handleClaimSubmission } from "./utilities/handleClaimSubmission.js";

// Add the event listener and call the new function
document.getElementById('submit-claim').addEventListener('click', handleClaimSubmission);