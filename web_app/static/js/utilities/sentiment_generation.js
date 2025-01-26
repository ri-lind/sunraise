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
        sentimentResult.textContent = "";
        sentimentIcon.textContent = "";

        const sentimentText = data.sentiment;
        const sentimentIconText = data.sentiment
          .toLowerCase()
          .includes("support")
          ? "✅"
          : data.sentiment.toLowerCase().includes("refute")
          ? "❌"
          : data.sentiment.toLowerCase().includes("neutral")
          ? "⚖️"
          : "❓";

        let index = 0;

        const typingInterval = setInterval(() => {
          if (index < sentimentText.length) {
            sentimentResult.textContent += sentimentText[index];
            index++;
          } else {
            clearInterval(typingInterval);
          }
        }, 10);

        sentimentIcon.textContent = sentimentIconText;

        const updatedText = sentimentText.split(".").slice(1).join(".").trim();
        setTimeout(() => {
          sentimentResult.textContent = updatedText;
        }, sentimentText.length * 50 + 500);
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
