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
        // Convert data keys (month, year tuples) into labels
        const monthNames = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ];

        const sortedData = Object.entries(data).sort(([a], [b]) => {
            // Extract year and month from the string keys
            const [monthA, yearA] = a.match(/\d+/g).map(Number);
            const [monthB, yearB] = b.match(/\d+/g).map(Number);
        
            // First compare years, then months if years are the same
            return yearA - yearB || monthA - monthB;
        });
        
        // Generate labels (e.g., "Jan 2025") in sorted order
        const labels = sortedData.map(([key]) => {
            const [month, year] = key.match(/\d+/g).map(Number);
            return `${monthNames[month - 1]} ${year}`;
        });
        
        // Extract scores in sorted order
        const scores = sortedData.map(([_, value]) => value);
        

        // Update the chart
        chart = new Chart(ctx, {
            type: 'line', // Example chart type
            data: {
                labels: labels, // Use the formatted labels
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
                            text: 'Month and Year',
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
