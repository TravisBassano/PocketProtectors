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
.banner {
  position: relative;
  width: 220px;
  min-height: 240px;
  padding: 1.2rem;
  color: white;
  background: #c00;           /* banner fill */
  border: 4px solid #900;     /* banner border */
  text-align: center;
  box-shadow: 0 6px 14px rgba(0,0,0,0.3);
  font-family: sans-serif;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  margin-bottom: 60px; /* room for the pennant tip */
  box-sizing: border-box;
}

/* Outer (border) triangle */
.banner::before {
  content: "";
  position: absolute;
  bottom: -44px;
  left: 0;
  width: 0;
  height: 0;
  border-left: 112px solid transparent;  /* (220px width + 2*4px border) / 2 */
  border-right: 112px solid transparent;
  border-top: 44px solid #900;  /* matches border color */
}

/* Inner (fill) triangle */
.banner::after {
  content: "";
  position: absolute;
  bottom: -40px;
  left: 0;
  width: 0;
  height: 0;
  border-left: 110px solid transparent;  /* (220px width) / 2 */
  border-right: 110px solid transparent;
  border-top: 40px solid #c00;  /* matches background */
}

.banner:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 18px rgba(0,0,0,0.4);
}

.banner-title {
  font-size: 1.1rem;
  margin-top: 0.5rem;
}

.banner-year {
  font-weight: 900;
  font-size: 1.6rem;
  margin-top: 1.2rem;
}

</style>