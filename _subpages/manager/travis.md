---
layout: page
title: Travis Profile Page
permalink: /manager/travis/
---

<div class="banner-wall">
  <div class="pennant">
    <h2>Consolation Bracket Champion</h2>
    <p>2018</p>
  </div>
  <div class="pennant">
    <h2>Most FAAB Wasted</h2>
    <p>2020</p>
  </div>
  <div class="pennant">
    <h2>Best Draft Name</h2>
    <p>2022</p>
  </div>
</div>

![Scatter plot]({{ site.baseurl }}/assets/plots/matchup_scatter_travis.png)

<style>
.banner-wall {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: center;
  padding: 2rem;
  background: #111; /* dark wall */
}

.pennant {
  width: 180px;
  background: #fff;
  border: 6px solid #c00; /* team color border */
  border-radius: 4px 4px 0 0; /* rounded top */
  text-align: center;
  padding: 1rem;
  font-family: 'Impact', sans-serif;
  position: relative;
  box-shadow: 0 6px 12px rgba(0,0,0,0.6);
}

/* Triangle bottom to make it look like a hanging pennant */
.pennant::after {
  content: "";
  position: absolute;
  bottom: -50px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 90px solid transparent;
  border-right: 90px solid transparent;
  border-top: 50px solid #fff;
  border-top-color: inherit; /* matches background */
}

.pennant h2 {
  font-size: 1rem;
  margin: 0;
  line-height: 1.2;
}

.pennant p {
  font-size: 1.4rem;
  font-weight: bold;
  margin: 0.5rem 0 0;
}
</style>