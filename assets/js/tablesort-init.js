// tablesort-init.js
document.addEventListener('DOMContentLoaded', function() {
  const table = document.getElementById('myTable');
  if (table) {
    new Tablesort(table);
  }
});