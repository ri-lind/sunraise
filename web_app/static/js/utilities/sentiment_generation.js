export function handleSentimentGeneration(claim) {
  fetch("/research_reengineering", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ claim }),
  })
    .then((response) => response.json())
    .then((data) => {
      const sentimentResult = document.getElementById("sentiment-result");
      const sentimentIcon = document.getElementById("sentiment-icon");

      if (data.sentiment) {
        const updatedText = data.sentiment.split(".").slice(1).join(".").trim();
        sentimentIcon.textContent = "❓";

        let index = 0;
        sentimentResult.textContent = ""; 
        const typingInterval = setInterval(() => {
          sentimentResult.textContent += updatedText.charAt(index);
          index++;
          if (index === updatedText.length) {
            clearInterval(typingInterval);

            if (data.sentiment.toLowerCase().includes("support")) {
              sentimentIcon.textContent = "✅";
            } else if (data.sentiment.toLowerCase().includes("refute")) {
              sentimentIcon.textContent = "❌";
            } else if (data.sentiment.toLowerCase().includes("neutral")) {
              sentimentIcon.textContent = "⚖️";
            } else {
              sentimentIcon.textContent = "❓";
            }
          }
        }, 10); 
      } else {
        sentimentResult.textContent = "No sentiment available.";
        sentimentIcon.textContent = "❓";
      }

      const tableBody = document
        .getElementById("research-table")
        .querySelector("tbody");
      tableBody.innerHTML = "";

      if (data.papers && data.papers.length > 0) {
        data.papers.forEach((paper) => {
          const icon = paper.support
            ? '<span style="color: green;">&#x2714;</span>'
            : '<span style="color: red;">&#x2716;</span>';
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
    .catch((err) => {
      console.error("Error:", err);
      alert("An error occurred. Please try again.");
    });
}
