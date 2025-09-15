// assets/js/tablesort-init.js

document.addEventListener('DOMContentLoaded', function() {
  const table = document.getElementById('myTable');
  if (!table) return;

  const ts = new Tablesort(table);

  // Clear all arrow classes
  function clearArrows() {
    table.querySelectorAll('th').forEach(th => {
      th.classList.remove('sort-up', 'sort-down');
    });
  }

  // Apply class to sorted header after sort
  table.addEventListener('tablesort:afterSort', function(event) {
    clearArrows();

    const th = event.target;
    if (ts.direction === 1) {
      th.classList.add('sort-up');
    } else if (ts.direction === -1) {
      th.classList.add('sort-down');
    }
  });
});
