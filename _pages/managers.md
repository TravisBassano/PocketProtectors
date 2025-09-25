---
layout: post
title: Manager Stats
permalink: /managers/
---

## League Managers

<div class="manager-grid">
  <a class="manager-card" href="{{ '/manager/bob/' | relative_url }}">Bob</a>
  <a class="manager-card" href="{{ '/manager/brendon/' | relative_url }}">Brendon</a>
  <a class="manager-card" href="{{ '/manager/brian/' | relative_url }}">Brian</a>
  <a class="manager-card" href="{{ '/manager/chris/' | relative_url }}">Chris</a>
  <a class="manager-card" href="{{ '/manager/eric/' | relative_url }}">Eric</a>
  <a class="manager-card" href="{{ '/manager/jordan/' | relative_url }}">Jordan</a>
  <a class="manager-card" href="{{ '/manager/keara/' | relative_url }}">Keara</a>
  <a class="manager-card" href="{{ '/manager/licata/' | relative_url }}">Licata</a>
  <a class="manager-card" href="{{ '/manager/mike/' | relative_url }}">Mike</a>
  <a class="manager-card" href="{{ '/manager/pj/' | relative_url }}">PJ</a>
  <a class="manager-card" href="{{ '/manager/ryan/' | relative_url }}">Ryan</a>
  <a class="manager-card" href="{{ '/manager/travis/' | relative_url }}">Travis</a>
</div>

## MVKC League History Plots

Here are some key visualizations exploring the history and performance of managers in the MVKC League.

### Manager Head-to-Head Record

This heatmap visualizes the win/loss record for every manager against every other manager, providing a quick way to see historical rivalries and dominant matchups.

![Manager head-to-head record heatmap]({{ site.baseurl }}/assets/plots/head_to_head_heatmap.png)

### Projected Points Analysis

The following plots analyze the difference between a manager's actual points and their projected points for each game.

![Manager projected points box plots]({{ site.baseurl }}/assets/plots/projected_pts_diff_box.png)
_Figure 2: A box plot showing the distribution of projected points differences for each manager._

![Manager projected points bar plots]({{ site.baseurl }}/assets/plots/projected_pts_diff_bar.png)
_Figure 3: A bar chart of the average projected points difference per manager._

### Win Percentage vs. Point Differential

This scatter plot shows a manager's overall win percentage against their average point differential. It can help identify managers who win games by a large margin versus those who consistently win close matchups.

![Manager win percentage vs. point diff]({{ site.baseurl }}/assets/plots/manager_win_vs_point_diff.png)

### Cumulative Points For (PF) and Points Against (PA) for all managers

![Manager cumulative PF PA bar plot]({{ site.baseurl }}/assets/plots/cumulative_performance_bar_plot.png)

### Manager Points Against vs. League Average by Season

![Manager points against vs. league season]({{ site.baseurl }}/assets/plots/seasonal_points_against_line_plot.png)

<style>
    .manager-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
    }

    .manager-card {
    display: block;
    text-align: center;
    padding: 0.8rem 1rem;
    background: linear-gradient(145deg, #ffffff, #f3f4f6);
    border-radius: 12px;
    font-weight: 600;
    color: #333;
    text-decoration: none;
    box-shadow: 0 3px 6px rgba(0,0,0,0.08);
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.3s;
    }

    .manager-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.12);
    background: linear-gradient(145deg, #f9fafb, #e5e7eb);
    color: #111;
    }
</style>