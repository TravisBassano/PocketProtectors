---
layout: page
title: Licata Profile Page
permalink: /manager/licata/
manager: Licata
---

<link rel="stylesheet" href="{{ '/assets/css/awards.css' | relative_url }}">

<script id="awards-data" type="application/json">
   {{ site.data.awards | jsonify }}
</script>

<div id="banner-wall" data-manager="{{ page.manager }}"></div>

<script src="{{ '/assets/js/manager-awards.js' | relative_url }}"></script>

![Scatter plot]({{ site.baseurl }}/assets/plots/matchup_scatter_licata.png)
