---
layout: default
title: Home
---

# Statistical League History
## 2018-2024

<link rel="stylesheet" href="{{ '/assets/css/tablesort.css' | relative_url }}">

<div class="table-responsive">
  <table id="myTable" class="table table-striped table-bordered table-hover sortable">
    <thead>
      <tr>
        <th>Manager</th>
        <th data-sort-method="number">Wins</th>
        <th data-sort-method="number">Losses</th>
        <th data-sort-method="dotsep">Win %</th>
        <th data-sort-method="dotsep">Points For (PF)</th>
        <th data-sort-method="dotsep">Points Against (PA)</th>
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
<script src="https://cdnjs.cloudflare.com/ajax/libs/tablesort/5.2.1/tablesort.min.js" integrity="sha512-F/gIMdDfda6OD2rnzt/Iyp2V9JLHlFQ+EUyixDg9+rkwjqgW1snpkpx7FD5FV1+gG2fmFj7I3r6ReQDUidHelA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/tablesort/5.2.1/sorts/tablesort.dotsep.min.js" integrity="sha512-4PQHFrJ/wVmBBE6FAFzkJJhjvIebDUZM0vTeGFsOSLxTPAP+CFEgt2HwDW/IQPttNDETeVRvBh11+vmF+lL9lQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

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