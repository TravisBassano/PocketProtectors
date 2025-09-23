---
layout: page
title: Travis Profile Page
permalink: /manager/travis/
---

<div class="banner-wall">
  <div class="banner banner-red">
    <div class="banner-title">Consolation Bracket Champion</div>
    <div class="banner-year">2018</div>
  </div>
  <div class="banner banner-blue">
    <div class="banner-title">Most FAAB Wasted</div>
    <div class="banner-year">2020</div>
  </div>
  <div class="banner banner-green">
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
  gap: 2.5rem; /* spacing between banners */
  padding: 2rem;
}

.banner {
  position: relative;
  width: 220px;
  height: 280px;
  padding: 1.2rem;
  color: white; /* text color */
  background: #c00; /* default: red team look */
  border: 4px solid #900; /* darker border for depth */
  text-align: center;
  box-shadow: 0 6px 14px rgba(0,0,0,0.3);
  font-family: sans-serif;
  font-weight: 600;
  clip-path: polygon(0 0, 100% 0, 100% 80%, 50% 100%, 0 80%);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
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

.banner-red { background: #c00; border-color: #900; }
.banner-blue { background: #0047ab; border-color: #002f6c; }
.banner-green { background: #007a33; border-color: #004d1a; }
.banner-purple { background: #5a2d82; border-color: #32184d; }

</style>