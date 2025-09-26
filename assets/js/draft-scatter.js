document.addEventListener("DOMContentLoaded", function () {
  // Load JSON data from the embedded <script>
  const rawData = JSON.parse(document.getElementById("draft-data").textContent);

  // Convert into Chart.js scatter dataset format
  const scatterData = rawData.map(d => ({
    x: d.player_cost,
    y: d.points,
    label: `${d.player_name} (${d.manager})`
  }));

  const ctx = document.getElementById("scatterChart").getContext("2d");

  new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [{
        label: "Players",
        data: scatterData,
        backgroundColor: "rgba(54, 162, 235, 0.6)",
        borderColor: "rgba(54, 162, 235, 1)"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              const d = context.raw;
              return `${d.label}: $${d.x} cost, ${d.y} points`;
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: "Player Cost" },
          grid: { color: "rgba(200,200,200,0.3)" },
          ticks: {
            callback: function (value) {
              return "$" + value; // Add dollar sign
            }
          }
        },
        y: {
          title: { display: true, text: "Points" },
          grid: { color: "rgba(200,200,200,0.3)" }
        }
      }
    }
  });
});
