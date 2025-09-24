// Wait for DOM to load
document.addEventListener("DOMContentLoaded", function() {

  const wall = document.getElementById("banner-wall");
  if (!wall) return;

  const manager = wall.dataset.manager.trim();

  const countsData = JSON.parse(document.getElementById("counts-data").textContent);

  const labels = countsData.map(item => item[0]);  // team names
  const counts = countsData.map(item => item[1]);  // counts

  const ctx = document.getElementById('favoriteTeams').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: `Favorite Teams for ${manager}`,
        data: counts,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        x: {
          title: {
            display: true,
            text: 'Team'
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Count'
          }
        }
      }
    }
  });
});