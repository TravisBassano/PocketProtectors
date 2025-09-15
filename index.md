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