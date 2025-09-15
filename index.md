---
layout: default
title: Home
---

## MVKC League History Dashboard

<div class="table-responsive">
  <table id="myTable" class="table table-striped table-bordered table-hover">
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

<style>
  /* Sort arrows with smooth transition */
  th {
    position: relative;
    cursor: pointer;
    user-select: none;
  }
  th:after {
    content: '⇅';
    font-size: 0.7em;
    position: absolute;
    right: 8px;
    color: #aaa;
    transition: transform 0.2s ease, color 0.2s ease;
  }
  th.tablesort-up:after {
    content: '↑';
    color: #007bff;
    transform: rotate(0deg);
  }
  th.tablesort-down:after {
    content: '↓';
    color: #007bff;
    transform: rotate(0deg);
  }

  /* Hover highlight */
  tbody tr:hover {
    background-color: #f1f1f1;
  }

  /* Zebra striping */
  tbody tr:nth-child(even) {
    background-color: #fafafa;
  }
</style>

<!-- Tablesort JS -->
<script src="https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js"></script>
<script>
  // Initialize Tablesort
  const table = document.getElementById('myTable');
  const ts = new Tablesort(table);

  // Optional: animate arrows smoothly
  table.querySelectorAll('th').forEach(th => {
    th.addEventListener('click', () => {
      // Remove classes from other headers
      table.querySelectorAll('th').forEach(other => {
        if (other !== th) {
          other.classList.remove('tablesort-up', 'tablesort-down');
        }
      });
    });
  });
</script>