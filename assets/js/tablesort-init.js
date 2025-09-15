// tablesort-init.js

document.addEventListener('DOMContentLoaded', function() {
  const table = document.getElementById('myTable');
  const ts = new Tablesort(table);

  // Remove arrow classes from all headers
  function clearArrowClasses() {
    table.querySelectorAll('th').forEach(th => {
      th.classList.remove('tablesort-up', 'tablesort-down');
    });
  }

  // Listen to sort event
  table.addEventListener('tablesort:afterSort', function(event) {
    clearArrowClasses();

    const th = event.target; // the column that was sorted
    if (ts.direction === 1) {
      th.classList.add('tablesort-up');
    } else if (ts.direction === -1) {
      th.classList.add('tablesort-down');
    }
  });
});

