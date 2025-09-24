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

<script id="counts-data" type="application/json">
  {{ site.data.team-counts | jsonify }}
</script>

<div id="banner-wall" data-manager="{{ page.manager }}"></div>

<script src="{{ '/assets/js/manager-awards.js' | relative_url }}"></script>

<div class="accolades">
  <div class="accolade draft">
    <div class="accolade-title">Best Draft</div>
    <div class="accolade-value">2021</div>
  </div>
  <div class="accolade mvp">
    <div class="accolade-title">Most Valuable Player</div>
    <div class="accolade-value">Jonathan Taylor</div>
  </div>
  <div class="accolade waiver">
    <div class="accolade-title">Best Waiver</div>
    <div class="accolade-value">Cordarrelle Patterson</div>
  </div>
</div>

<script src="{{ '/assets/js/team-counts.js' | relative_url }}"></script>


![Scatter plot]({{ site.baseurl }}/assets/plots/matchup_scatter_travis.png)