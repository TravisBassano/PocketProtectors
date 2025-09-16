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
<script src="{{ '/assets/js/manager-chart.js' | relative_url }}"></script>