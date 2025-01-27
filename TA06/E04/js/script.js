// Placeholder de datos sobre lluvias promedio en España
const labels = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const data = {
    labels: labels,
    datasets: [{
        label: 'Precipitaciones promedio (mm)',
        data: [50, 45, 60, 80, 100, 75, 40, 30, 60, 90, 110, 120], // Datos de ejemplo
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderWidth: 1
    }]
};

const config = {
    type: 'bar',
    data: data,
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 20
                }
            }
        },
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                enabled: true
            }
        }
    }
};

const ctx = document.getElementById('rainfallChart').getContext('2d');
const rainfallChart = new Chart(ctx, config);