---
layout: post
title: Draft Results
permalink: /draft/
---

<div id="season-filters" class="season-filters">
</div>

<canvas id="scatterChart" width="600" height="400"></canvas>

<script id="draft-data" type="application/json">
  {{ site.data.draft-results | jsonify }}
</script>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="{{ '/assets/js/draft-scatter.js' | relative_url }}"></script>

<style>
  .season-filters {
  margin-bottom: 1rem;
}

.season-filters label {
  display: inline-block;
  background: #f0f0f0;
  border-radius: 25px;
  padding: 5px 12px;
  margin: 3px;
  cursor: pointer;
  font-size: 0.9rem;
}

.season-filters input[type="checkbox"] {
  display: none;
}

.season-filters input[type="checkbox"]:checked + span {
  background: #007bff;
  color: #fff;
}
</style>