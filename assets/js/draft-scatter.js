document.addEventListener("DOMContentLoaded", function () {
  // Load JSON data from the embedded <script>
  const rawData = JSON.parse(document.getElementById("draft-data").textContent);

    // Group data by manager
  const grouped = {};
  rawData.forEach(d => {
    if (!grouped[d.manager]) {
      grouped[d.manager] = [];
    }
    grouped[d.manager].push({
      x: d.player_cost,
      y: d.points,
      label: `${d.player_name} (${d.player_pos})`
    });
  });

  // Assign colors (loop if more managers than colors)
  const colors = [
    "rgba(54, 162, 235, 0.7)",   // blue
    "rgba(255, 99, 132, 0.7)",   // red
    "rgba(255, 206, 86, 0.7)",   // yellow
    "rgba(75, 192, 192, 0.7)",   // teal
    "rgba(153, 102, 255, 0.7)",  // purple
    "rgba(255, 159, 64, 0.7)",   // orange
    "rgba(199, 199, 199, 0.7)",  // gray
    "rgba(255, 99, 255, 0.7)",   // magenta
    "rgba(99, 255, 132, 0.7)",   // green
    "rgba(99, 132, 255, 0.7)",   // light blue
    "rgba(255, 219, 102, 0.7)",  // gold
    "rgba(102, 255, 219, 0.7)"   // aqua
  ];

  const datasets = Object.keys(grouped).map((manager, i) => ({
    label: manager,
    data: grouped[manager],
    backgroundColor: colors[i % colors.length],
    borderColor: colors[i % colors.length].replace("0.6", "1"),
    pointRadius: 6
  }));

  const ctx = document.getElementById("scatterChart").getContext("2d");

  new Chart(ctx, {
    type: "scatter",
    data: { datasets },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              const d = context.raw;
              return `${d.label} – $${d.x} cost, ${d.y} points`;
            }
          }
        },
        legend: {
          position: "top"
        }
      },
      scales: {
        x: {
          title: { display: true, text: "Player Cost" },
          grid: { color: "rgba(200,200,200,0.3)" },
          ticks: {
            callback: function (value) {
              return "$" + value; // Dollar sign
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