---
layout: page
title: Travis Profile Page
permalink: /manager/travis/
---

<div class="banner">
  <div class="banner-content">
    <div class="banner-title">League Champion</div>
    <div class="banner-year">2021</div>
  </div>

  <!-- Inline SVG laurel -->
  <svg class="banner-laurel banner--gold" viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <g fill="currentColor">
      <!-- Left side -->
      <path d="M50 95c-15-20-20-40-18-55 1-8 4-15 8-20-6 2-11 7-14 13-4 8-5 18-4 28 2 15 9 29 22 41z"/>
      <!-- Right side -->
      <path d="M150 95c15-20 20-40 18-55-1-8-4-15-8-20 6 2 11 7 14 13 4 8 5 18 4 28-2 15-9 29-22 41z"/>
    </g>
  </svg>
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

/* Laurel placement */
.banner-laurel {
  position: absolute;
  left: 50%;
  bottom: 12%;
  transform: translateX(-50%);
  width: 65%;
  max-width: 180px;
  height: auto;
  opacity: 0.12;
  z-index: 1;
  pointer-events: none;
}

/* Themed variants */
.banner--gold {
  background: #caa200;
  border-color: #9d7f00;
  color: #fff7d1;    /* laurel + text color */
}

.banner--silver {
  background: #aaa;
  border-color: #777;
  color: #f0f0f0;
}

.banner--bronze {
  background: #b87333;
  border-color: #814c1f;
  color: #ffe6d1;
}

.banner:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 18px rgba(0,0,0,0.4);
}

</style>