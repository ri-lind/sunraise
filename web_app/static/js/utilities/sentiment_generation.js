// Define the function to handle sentiment generation
export function handleSentimentGeneration(claim) {
    fetch('/research_reengineering', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claim })
    })
    .then(response => response.json())
    .then(data => {
        // Handle sentiment result with icon
        const sentimentResult = document.getElementById('sentiment-result');
        const sentimentIcon = document.getElementById('sentiment-icon');

        if (data.sentiment) {
            sentimentResult.textContent = data.sentiment;
            console.log(data.sentiment.toLowerCase())
            // Update the icon based on sentiment
            if (data.sentiment.toLowerCase().includes('support')) {
                sentimentIcon.textContent = '✅'; // Happy face for positive sentiment
            } else if (data.sentiment.toLowerCase().includes('refute')) {
                sentimentIcon.textContent = '❌'; // Sad face for negative sentiment
            } else if (data.sentiment.toLowerCase().includes('neutral')) {
                sentimentIcon.textContent = '⚖️'; // Neutral face
            } else {
                sentimentIcon.textContent = '❓'; // Unknown sentiment
            }

            // Split the text into sentences, remove the first, and join the rest
            const updatedText = fullText.split('.').slice(1).join('.').trim();

            // Update the text content
            sentimentResult.textContent = updatedText;
        } else {
            sentimentResult.textContent = "No sentiment available.";
            sentimentIcon.textContent = '❓';
        }

        // Populate the research table
        const tableBody = document.getElementById('research-table').querySelector('tbody');
        tableBody.innerHTML = ''; // Clear existing rows

        if (data.papers && data.papers.length > 0) {
            data.papers.forEach(paper => {
                const icon = paper.support ? 
                '<span style="color: green;">&#x2714;</span>' : 
                '<span style="color: red;">&#x2716;</span>';
                const row = `
                    <tr>
                        <td>${paper.title}</td>
                        <td>${icon}</td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });
        } else {
            const row = '<tr><td colspan="3">No research papers found.</td></tr>';
            tableBody.innerHTML = row;
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('An error occurred. Please try again.');
    });
}