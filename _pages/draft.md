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
  cursor: pointer;
  margin: 3px;
}

.season-filters input[type="checkbox"] {
  display: none; /* hide the real checkbox */
}

.season-filters span {
  display: inline-block;
  background: #f0f0f0;
  border-radius: 25px;
  padding: 6px 14px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.season-filters input[type="checkbox"]:checked + span {
  background: #007bff;
  color: #fff;
}
</style>