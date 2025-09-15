---
layout: default
title: Home
---

## MVKC League History Dashboard

<link rel="stylesheet" href="{{ '/assets/css/tablesort.css' | relative_url }}">

<div class="table-responsive">
  <table id="myTable" class="table table-striped table-bordered table-hover sortable">
    <thead>
      <tr>
        <th>Manager</th>
        <th data-sort-method="number">Wins</th>
        <th data-sort-method="number">Losses</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Bob</td><td>47</td><td>48</td></tr>
      <tr><td>Brendon</td><td>61</td><td>34</td></tr>
      <tr><td>Brian</td><td>47</td><td>48</td></tr>
      <tr><td>Chris</td><td>34</td><td>61</td></tr>
      <tr><td>Eric</td><td>40</td><td>55</td></tr>
      <tr><td>Jordan</td><td>50</td><td>45</td></tr>
      <tr><td>Keara</td><td>47</td><td>48</td></tr>
      <tr><td>Licata</td><td>52</td><td>43</td></tr>
      <tr><td>Mike</td><td>53</td><td>42</td></tr>
      <tr><td>PJ</td><td>50</td><td>45</td></tr>
      <tr><td>Ryan</td><td>47</td><td>48</td></tr>
      <tr><td>Travis</td><td>42</td><td>53</td></tr>
    </tbody>
  </table>
</div>

<!-- Tablesort JS -->
<script src="https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js"></script>

<script>
  new Tablesort(document.getElementById('myTable'));
</script>