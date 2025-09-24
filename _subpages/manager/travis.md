---
layout: page
title: Travis Profile Page
permalink: /manager/travis/
---

<div class="banner banner--gold">
  <div class="banner-content">
    <div class="banner-title">League Champion</div>
    <div class="banner-year">2021</div>
    <div class="star star--gold"></div>
  </div>
</div>

<div class="banner banner--silver">
  <div class="banner-content">
    <div class="banner-title">League Runner Up</div>
    <div class="banner-year">2022</div>
    <div class="star star--silver"></div>
  </div>
</div>

<div class="banner banner--bronze">
  <div class="banner-content">
    <div class="banner-title">League Member</div>
    <div class="banner-year">2023</div>
    <div class="star star--bronze"></div>
  </div>
</div>


![Scatter plot]({{ site.baseurl }}/assets/plots/matchup_scatter_travis.png)

<style>
.banner {
  position: relative;
  width: 200px;
  min-height: 275px;
  padding: 1.1rem 1.4rem;
  background: #222;
  border: 4px solid #111;
  color: white;               /* text color also drives SVG color */
  text-align: center;
  overflow: hidden;
  border-radius: 6px;
  background: #02008aff;
  border-color: #353535ff;
  box-shadow: 0 6px 14px rgba(0,0,0,0.18);
  font-family: system-ui, sans-serif;
  margin: 1.75em;
}

.banner-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.banner-title {
  margin-top: 0.25rem;
  font-size: 1.05rem;
  font-weight: 600;
}

.banner-year {
  margin-top: auto;
  margin-bottom: 1.6rem;
  font-weight: 800;
  font-size: 1.65rem;
  z-index: 2;
}

.star {
  width: 100px;
  height: 100px;
  background-color: #FFD700;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, 50%);

  /* The clip-path polygon defines the star shape */
  clip-path: polygon(
    50% 0%,
    61.8% 38.2%,
    100% 38.2%,
    69.1% 61.8%,
    80.9% 100%,
    50% 76.4%,
    19.1% 100%,
    30.9% 61.8%,
    0% 38.2%,
    38.2% 38.2%
  );
}

/* Themed variants */
.banner--gold {
  border-color: #caa200;
  color: #fff7d1;    /* laurel + text color */
}

.banner--silver {
  border-color: #aaaaaaff;
  color: #f0f0f0;
}

.banner--bronze {
  border-color: #b87333;
  color: #ffe6d1;
}

.star--gold {
  background-color: #caa200;
  color: #caa200;
}

.star--silver {
  background-color: #aaaaaaff;
  color: #aaaaaaff;
}

.star--bronze {
  background-color: #b87333;
  color: #b87333;
}

.banner:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 18px rgba(0,0,0,0.4);
}

</style>