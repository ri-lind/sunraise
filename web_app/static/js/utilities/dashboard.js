import { getRandomNumbers } from "./misc.js";



let chart;
// Function to initialize the chart
export function initializeChart() {
    const ctx = document.getElementById('chart').getContext('2d'); // Get the canvas context
    chart = new Chart(ctx, {
        type: 'line', // Example chart type
        data: {
            labels: ['2019', '2020', '2021', '2022', '2023'], // Example years
            datasets: [{
                label: 'Average Scores',
                data: getRandomNumbers(5), // random data
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Year',
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: 'Average Score',
                    },
                    min: 0,
                    max: 5,
                },
            },
        }
    });
}
export function updateDashboard(claim) {
    if (chart) {
        chart.destroy();
    }

    const canvas = document.getElementById('chart'); // Get the canvas element
    canvas.width = canvas.parentElement.offsetWidth; // Set width to match parent container
    canvas.height = canvas.parentElement.offsetHeight; // Set height to match parent container
    const ctx = document.getElementById('chart').getContext('2d'); // Get the canvas context

    fetch('/generate_dashboard', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // Specify JSON content type
        },
        body: JSON.stringify({ claim }) // Send the claim in the request body
    })
    .then(response => response.json())
    .then(data => {
        // Convert the month numbers to month names
        const monthNames = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ];

        // Extract labels (month names) and data (average scores)
        const labels = Object.keys(data).map(month => monthNames[parseInt(month) - 1]);
        const scores = Object.values(data);

        // Update the chart
        chart = new Chart(ctx, {
            type: 'line', // Example chart type
            data: {
                labels: labels, // Use the month names as labels
                datasets: [{
                    label: 'Average Scores',
                    data: scores, // Use the scores from the backend
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Month',
                        },
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Average Score',
                        },
                        min: 0,
                        max: 5,
                    },
                },
            }
        });
    })
    .catch(error => {
        console.error('Error updating the dashboard:', error);
        alert('Failed to update the dashboard. Please try again.');
    });
}
