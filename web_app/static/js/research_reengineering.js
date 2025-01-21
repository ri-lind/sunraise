import { handleSentimentGeneration } from 'utilities/sentiment_generation.js';
// Add the event listener and call the new function
document.getElementById('submit-claim').addEventListener('click', handleSentimentGeneration);
