document.addEventListener('DOMContentLoaded', function () {
    const csvPath = './TA06/E03/output/stats/annual_precipitation_summary_20250204_124219.csv'; // Ruta del archivo CSV en nuestro proyecto

    fetch(csvPath)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.text();
        })
        .then(data => {
            console.log('CSV Data:', data); // Log CSV data
            const parsedData = Papa.parse(data, { header: true }).data;
            console.log('Parsed Data:', parsedData); // Log parsed data

            const years = parsedData.map(row => row['Year']);
            const avgRainfall = parsedData.map(row => parseFloat(row['Average Rainfall']));
            const maxRainfall = parsedData.map(row => parseFloat(row['Max Rainfall']));
            const minRainfall = parsedData.map(row => parseFloat(row['Min Rainfall']));
            const stdDev = parsedData.map(row => parseFloat(row['Std Dev']));

            const ctx = document.getElementById('rainfallChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: years,
                    datasets: [
                        {
                            label: 'Average Rainfall',
                            data: avgRainfall,
                            borderColor: 'blue',
                            backgroundColor: 'rgba(0, 0, 255, 0.1)',
                            fill: false,
                            pointHoverBackgroundColor: 'rgba(0, 0, 139, 0.8)',
                            pointHoverBorderColor: 'rgba(0, 0, 139, 0.8)'
                        },
                        {
                            label: 'Max Rainfall',
                            data: maxRainfall,
                            borderColor: 'red',
                            backgroundColor: 'rgba(255, 0, 0, 0.1)',
                            fill: false,
                            pointHoverBackgroundColor: 'rgba(139, 0, 0, 0.8)',
                            pointHoverBorderColor: 'rgba(139, 0, 0, 0.8)'
                        },
                        {
                            label: 'Min Rainfall',
                            data: minRainfall,
                            borderColor: 'purple',
                            backgroundColor: 'rgba(128, 0, 128, 0.1)',
                            fill: false,
                            pointHoverBackgroundColor: 'rgba(75, 0, 130, 0.8)',
                            pointHoverBorderColor: 'rgba(75, 0, 130, 0.8)'
                        },
                        {
                            label: 'Std Dev',
                            data: stdDev,
                            borderColor: 'orange',
                            backgroundColor: 'rgba(255, 165, 0, 0.1)',
                            fill: false,
                            pointHoverBackgroundColor: 'rgba(255, 140, 0, 0.8)',
                            pointHoverBorderColor: 'rgba(255, 140, 0, 0.8)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: 'Annual Precipitation Statistics'
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Year'
                            },
                            gridLines: {
                                display: false
                            }
                        }],
                        yAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Rainfall (mm)'
                            },
                            gridLines: {
                                display: false
                            }
                        }]
                    }
                }
            });

            // Fill the table with data
            const tableBody = document.getElementById('dataTable').querySelector('tbody');
            parsedData.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row['Year']}</td>
                    <td>${row['Average Rainfall']}</td>
                    <td>${row['Max Rainfall']}</td>
                    <td>${row['Min Rainfall']}</td>
                    <td>${row['Std Dev']}</td>
                    <td>${row['Variability Index']}</td>
                `;
                tableBody.appendChild(tr);
            });

            // Handle CSV download
            document.getElementById('downloadCsv').addEventListener('click', () => {
                const blob = new Blob([data], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = 'annual_precipitation_summary.csv';
                link.click();
            });
        })
        .catch(error => {
            console.error('Error fetching the CSV file:', error);
        });
});