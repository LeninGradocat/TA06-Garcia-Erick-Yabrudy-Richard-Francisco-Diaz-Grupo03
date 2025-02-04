document.addEventListener('DOMContentLoaded', function () {
    const csvPath = './output/stats/annual_precipitation_summary_20250101_000000.csv'; // Cambia la ruta según sea necesario

    fetch(csvPath)
        .then(response => response.text())
        .then(data => {
            const parsedData = Papa.parse(data, { header: true }).data;
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

            // Llenar la tabla con los datos
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

            // Manejar la descarga del CSV
            document.getElementById('downloadCsv').addEventListener('click', () => {
                const blob = new Blob([data], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = 'annual_precipitation_summary.csv';
                link.click();
            });
        });
});