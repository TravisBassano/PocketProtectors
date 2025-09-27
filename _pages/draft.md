---
layout: post
title: Draft Results
permalink: /draft/
---

## Player Auction Draft Cost vs Points Scored as Starter for Drafting Team
### Filterable by season and manager

<div id="season-filters" class="season-filters">
</div>

<div class="chart-container">
  <canvas id="scatterChart" width="600" height="400"></canvas>
</div>


<script id="draft-data" type="application/json">
  {{ site.data.draft-results | jsonify }}
</script>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="{{ '/assets/js/draft-scatter.js' | relative_url }}"></script>

<style>
.season-filters {
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  margin: 1rem 0;
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
  text-decoration: line-through;
}

.season-filters input[type="checkbox"]:checked + span {
  background: #007bff;
  color: #fff;
  text-decoration: none;
}

  .chart-container {
    position: relative;
    width: 100%;
    height: 300px; /* adjust for your needs */
    }

  @media (max-width: 600px) {
  .chart-container {
        height: 280px; /* smaller for portrait phones */
    }
    }

</style>