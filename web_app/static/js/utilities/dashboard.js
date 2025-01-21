export function updateDashboard() {
    fetch('/generate_dashboard', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        // Update the chart with new data
        myChart.data.labels = data.labels;
        myChart.data.datasets = data.datasets;
        myChart.update(); // Refresh the chart
    })
    .catch(error => {
        console.error('Error updating the dashboard:', error);
        alert('Failed to update the dashboard. Please try again.');
    });
}