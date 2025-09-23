---
layout: page
title: Travis Profile Page
permalink: /manager/travis/
---

<div class="banner-wall">
  <div class="banner">
    <div class="banner-title">Consolation Bracket Champion</div>
    <div class="banner-year">2018</div>
  </div>
  <div class="banner">
    <div class="banner-title">Most FAAB Wasted</div>
    <div class="banner-year">2020</div>
  </div>
  <div class="banner">
    <div class="banner-title">Best Draft Name</div>
    <div class="banner-year">2022</div>
  </div>
</div>

![Scatter plot]({{ site.baseurl }}/assets/plots/matchup_scatter_travis.png)

<style>
.banner-wall {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem; /* spacing between banners */
  padding: 2rem;
}

.banner {
  position: relative;
  width: 180px;
  padding: 1rem 1.5rem 2.5rem; /* extra padding for the V bottom */
  background: white;
  border: 3px solid #c00;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  font-family: sans-serif;
  font-weight: 600;
  clip-path: polygon(0 0, 100% 0, 100% 85%, 50% 100%, 0 85%);
  /* makes the V-shape cut */
}

.banner-title {
  font-size: 0.95rem;
}

.banner-year {
  font-weight: 800;
  font-size: 1.2rem;
  margin-top: 0.5rem;
}
</style>