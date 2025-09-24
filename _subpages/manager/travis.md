---
layout: page
title: Travis Profile Page
permalink: /manager/travis/
manager: Travis
---

<link rel="stylesheet" href="{{ '/assets/css/awards.css' | relative_url }}">

<script id="awards-data" type="application/json">
  {{ site.data.awards | jsonify }}
</script>

<script id="accolades-data" type="application/json">
  {{ site.data.accolades | jsonify }}
</script>

<script id="counts-data" type="application/json">
  {{ site.data.team-counts | jsonify }}
</script>

<div id="banner-wall" data-manager="{{ page.manager }}"></div>

<script src="{{ '/assets/js/manager-awards.js' | relative_url }}"></script>

<div id="accolades-wall"></div>

<canvas id="favoriteTeams"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="{{ '/assets/js/team-counts.js' | relative_url }}"></script>


![Scatter plot]({{ site.baseurl }}/assets/plots/matchup_scatter_travis.png)