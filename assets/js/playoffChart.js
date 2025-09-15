// assets/js/playoffChart.js

document.addEventListener("DOMContentLoaded", function() {
  const managers = JSON.parse(document.getElementById('playoff-data').textContent);

  // Match chart font to site CSS
  Chart.defaults.font.family = getComputedStyle(document.body).getPropertyValue("font-family");
  Chart.defaults.font.size = parseInt(getComputedStyle(document.body).getPropertyValue("font-size"));

  const labels = managers.map(m => m.manager);
  const playoffAppearances = managers.map(m => m.playoff_appearances);
  const championshipAppearances = managers.map(m => m.championship_appearances);
  const championships = managers.map(m => m.championships);

  const data = {
    labels: labels,
    datasets: [
      {
        label: 'Playoff Appearances',
        data: playoffAppearances,
        backgroundColor: 'rgba(54, 162, 235, 0.7)'
      },
      {
        label: 'Championship Appearances',
        data: championshipAppearances,
        backgroundColor: 'rgba(255, 206, 86, 0.7)'
      },
      {
        label: 'Championships',
        data: championships,
        backgroundColor: 'rgba(75, 192, 192, 0.7)'
      }
    ]
  };

  const config = {
    type: 'bar',
    data: data,
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        title: { display: true, text: 'Fantasy Manager Playoff Stats' }
      },
      scales: {
        y: {
            beginAtZero: true,
            ticks: {
                precision: 0
            }
        }
      }
    }
  };

  new Chart(
    document.getElementById('playoffChart'),
    config
  );
});