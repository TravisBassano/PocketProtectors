// tablesort-init.js

document.addEventListener('DOMContentLoaded', function() {
  // Initialize Tablesort
  const table = document.getElementById('myTable');
  new Tablesort(table);

  // Ensure only clicked header shows arrow state
  table.querySelectorAll('th').forEach(th => {
    th.addEventListener('click', () => {
      table.querySelectorAll('th').forEach(other => {
        if (other !== th) {
          other.classList.remove('tablesort-up', 'tablesort-down');
        }
      });
    });
  });
});
