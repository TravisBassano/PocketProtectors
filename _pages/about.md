---
layout: page
title: About
permalink: /about/
---

# Fantasy Manager Stats

<select id="manager-select">
  <option value="Bob">Bob</option>
  <option value="Brendon">Brendon</option>
  <option value="Brian">Brian</option>
  <option value="Chris">Chris</option>
  <option value="Eric">Eric</option>
  <option value="Jordan">Jordan</option>
  <option value="Keara">Keara</option>
  <option value="Licata">Licata</option>
  <option value="Mike">Mike</option>
  <option value="PJ">PJ</option>
  <option value="Ryan">Ryan</option>
  <option value="Travis">Travis</option>
</select>

<canvas id="managerChart" width="600" height="400"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Load data from Jekyll _data/managers.yml
const managerData = {
  {% for manager, stats in site.data.seasons %}
  "{{ manager }}": {
    pf: {{ stats.pf }},
    pa: {{ stats.pa }}
  }{% if forloop.last == false %},{% endif %}
  {% endfor %}
};

// Initial chart
const ctx = document.getElementById('managerChart').getContext('2d');
let currentManager = document.getElementById('manager-select').value;

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
    plugins: {
      legend: { position: 'top' }
    },
    scales: {
      y: { beginAtZero: true, ticks: { stepSize: 10 } }
    }
  }
};

const managerChart = new Chart(ctx, chartConfig);

// Update chart on manager select
document.getElementById('manager-select').addEventListener('change', (e) => {
  const selected = e.target.value;
  managerChart.data.datasets[0].data = managerData[selected].pf;
  managerChart.data.datasets[1].data = managerData[selected].pa;
  managerChart.update();
});
</script>
