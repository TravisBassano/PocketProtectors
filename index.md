---
layout: default
title: Home
---

## MVKC League History Dashboard

<link rel="stylesheet" href="{{ '/assets/css/tablesort.css' | relative_url }}">

<div class="table-responsive">
  <table id="myTable" class="table table-striped table-bordered table-hover sortable">
    <thead>
      <tr>
        <th>Manager</th>
        <th data-sort-method="number">Wins</th>
        <th data-sort-method="number">Losses</th>
        <th data-sort-method="number">Win %</th>
        <th data-sort-method="number">Points For (PF)</th>
        <th data-sort-method="number">Points Against (PA)</th>
      </tr>
    </thead>
    <tbody>
      {% for manager in site.data.overall %}
      <tr>
        <td>{{ manager.name }}</td>
        <td>{{ manager.wins }}</td>
        <td>{{ manager.losses }}</td>
        <td>{{ manager.win_pct }}</td>
        <td>{{ manager.pf }}</td>
        <td>{{ manager.pa }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<!-- Tablesort JS -->
<script src="https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js"></script>

<script>
  new Tablesort(document.getElementById('myTable'));
</script>


<canvas id="playoffChart" width="800" height="400"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  const managers = {{ site.data.playoffs | jsonify }};

  const labels = managers.map(m => m.manager);
  const playoffAppearances = managers.map(m => m.playoff_appearances);
  const championshipAppearances = managers.map(m => m.championship_appearances);
  const championships = managers.map(m => m.championships);

  const data = {
    labels: labels,
    datasets: [
      {
        label: 'Playoff Appearances',
        data: playoffAppearances,
        backgroundColor: 'rgba(54, 162, 235, 0.7)'
      },
      {
        label: 'Championship Appearances',
        data: championshipAppearances,
        backgroundColor: 'rgba(255, 206, 86, 0.7)'
      },
      {
        label: 'Championships',
        data: championships,
        backgroundColor: 'rgba(75, 192, 192, 0.7)'
      }
    ]
  };

  const config = {
    type: 'bar',
    data: data,
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        title: { display: true, text: 'Fantasy Manager Playoff Stats' }
      },
      scales: {
        y: { beginAtZero: true, precision: 0 }
      }
    }
  };

  new Chart(
    document.getElementById('playoffChart'),
    config
  );
</script>