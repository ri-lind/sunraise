document.getElementById('submit-claim').addEventListener('click', () => {
    const claim = document.getElementById('user-claim').value.trim();
    if (claim) {
        fetch('/research_reengineering', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim })
        })
        .then(response => response.json())
        .then(data => {
            // Handle sentiment result
            const sentimentResult = document.getElementById('sentiment-result');
            sentimentResult.textContent = data.sentiment || "No sentiment available.";

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
    } else {
        alert('Please enter a claim.');
    }
});