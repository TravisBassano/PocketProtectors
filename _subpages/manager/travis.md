---
layout: page
title: Travis Profile Page
permalink: /manager/travis/
---

<div class="banner-wall">
  <div class="banner">
    <h2>Consolation Bracket Champion</h2>
    <p>2018</p>
  </div>
  <div class="banner">
    <h2>Most FAAB Wasted</h2>
    <p>2020</p>
  </div>
  <div class="banner">
    <h2>Best Draft Name</h2>
    <p>2022</p>
  </div>
</div>

![Scatter plot]({{ site.baseurl }}/assets/plots/matchup_scatter_travis.png)

<style>
    .banner-wall {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  justify-content: center;
  padding: 2rem;
  background: #1a1a1a; /* dark backdrop like a stadium wall */
}

.banner {
  width: 180px;
  background: #fff;
  color: #111;
  border: 4px solid #c00;
  border-radius: 8px;
  text-align: center;
  padding: 1rem;
  font-family: 'Impact', sans-serif;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  position: relative;
}

.banner::before {
  content: "";
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-bottom: 20px solid #c00; /* “hanger” triangle */
}

.banner h2 {
  font-size: 1rem;
  margin: 0;
  line-height: 1.2;
}

.banner p {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0.5rem 0 0;
}
</style>