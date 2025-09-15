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
        <td>{{ manager.pf | round: 1 }}</td>
        <td>{{ manager.pa | round: 1 }}</td>
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

<!-- Embed data in a hidden element -->
<script id="playoff-data" type="application/json">
  {{ site.data.playoffs | jsonify }}
</script>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="{{ '/assets/js/playoffChart.js' | relative_url }}"></script>