import { handleSentimentGeneration } from './utilities/sentiment_generation.js';
import { updateDashboard } from './utilities/dashboard.js';

// Add the event listener and call the new function
document.getElementById('submit-claim').addEventListener('click', handleSentimentGeneration);
document.getElementById('submit-claim').addEventListener('click', updateDashboard);
