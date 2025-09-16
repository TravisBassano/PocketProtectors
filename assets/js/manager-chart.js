// Load manager data from Jekyll _data/seasons
const managerData = {
  {% for manager in site.data.seasons %}
  "{{ manager }}": {
    pf: {{ site.data.seasons[manager].pf | jsonify }},
    pa: {{ site.data.seasons[manager].pa | jsonify }}
  }{% if forloop.last == false %},{% endif %}
  {% endfor %}
};

// Wait for DOM to load
document.addEventListener("DOMContentLoaded", function() {
  const ctx = document.getElementById('managerChart').getContext('2d');
  const managerSelect = document.getElementById('manager-select');
  let currentManager = managerSelect.value;

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
      scales: { y: { beginAtZero: true, ticks: { stepSize: 10 } } }
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