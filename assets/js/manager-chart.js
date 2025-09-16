// Wait for DOM to load
document.addEventListener("DOMContentLoaded", function() {
  const ctx = document.getElementById('managerChart').getContext('2d');
  const managerSelect = document.getElementById('manager-select');
  const managerData = JSON.parse(document.getElementById("manager-data").textContent);
  let currentManager = managerSelect.value;

  const allPf = Object.values(managerData).flatMap(m => m.pf);
  const allPa = Object.values(managerData).flatMap(m => m.pa);

  const stepSize = 100;

  let globalMin = Math.min(...allPf, ...allPa);
  let globalMax = Math.max(...allPf, ...allPa);

  globalMin = Math.ceil(globalMin / stepSize) * stepSize;
  globalMax = Math.ceil(globalMax / stepSize) * stepSize;

  const chartConfig = {
    type: 'line',
    data: {
      labels: ['2018', '2019', '2020', '2021', '2022', '2023', '2024'],
      datasets: [
        {
          label: 'Points Scored',
          data: managerData[currentManager].pf,
          borderColor: 'green',
          fill: false,
        },
        {
          label: 'Points Against',
          data: managerData[currentManager].pa,
          borderColor: 'red',
          fill: false,
        }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'top' } },
      scales: { y: { beginAtZero: true, min: globalMin, max: globalMax, ticks: { stepSize: stepSize } } }
    }
  };

  const managerChart = new Chart(ctx, chartConfig);

  // Update chart when manager selection changes
  managerSelect.addEventListener('change', (e) => {
    const selected = e.target.value;
    managerChart.data.datasets[0].data = managerData[selected].pf;
    managerChart.data.datasets[1].data = managerData[selected].pa;
    managerChart.update();
  });
});