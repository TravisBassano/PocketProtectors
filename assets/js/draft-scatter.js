document.addEventListener("DOMContentLoaded", function () {
  const rawData = JSON.parse(document.getElementById("draft-data").textContent);

  // Get unique seasons
  const seasons = [...new Set(rawData.map(d => d.season))].sort();

  // Build pill checkboxes
  const filterDiv = document.getElementById("season-filters");
  seasons.forEach(season => {
    const id = "season-" + season;
    const label = document.createElement("label");
    label.innerHTML = `
      <input type="checkbox" id="${id}" value="${season}" checked>
      <span>${season}</span>
    `;
    filterDiv.appendChild(label);
  });

  // Colors for managers
  const colors = [
    "rgba(54, 162, 235, 0.7)",
    "rgba(255, 99, 132, 0.7)",
    "rgba(255, 206, 86, 0.7)",
    "rgba(75, 192, 192, 0.7)",
    "rgba(153, 102, 255, 0.7)",
    "rgba(255, 159, 64, 0.7)",
    "rgba(199, 199, 199, 0.7)",
    "rgba(255, 99, 255, 0.7)",
    "rgba(99, 255, 132, 0.7)",
    "rgba(99, 132, 255, 0.7)",
    "rgba(255, 219, 102, 0.7)",
    "rgba(102, 255, 219, 0.7)"
  ];

  const markers = [
    "circle",
    "triangle",
    "rect",
    "cross"
  ];

  const ctx = document.getElementById("scatterChart").getContext("2d");

  let chart = new Chart(ctx, {
    type: "scatter",
    data: { datasets: [] },
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
            position: "top",
            labels: {
            usePointStyle: true,
            boxWidth: 10
            }
        },
      },
      scales: {
        x: {
          title: { display: true, text: "Player Cost" },
          grid: { color: "rgba(200,200,200,0.3)" },
          ticks: {
            callback: value => "$" + value
          }
        },
        y: {
          title: { display: true, text: "Points" },
          grid: { color: "rgba(200,200,200,0.3)" }
        }
      }
    }
  });

  // Function to rebuild datasets based on selected seasons
  function updateChart() {
    const checkedSeasons = Array.from(filterDiv.querySelectorAll("input:checked"))
      .map(cb => parseInt(cb.value));

    // Group by manager but filter seasons first
    const grouped = {};
    rawData.forEach(d => {
      if (!checkedSeasons.includes(d.season)) return;
      if (!grouped[d.manager]) grouped[d.manager] = [];
      grouped[d.manager].push({
        x: d.player_cost,
        y: d.points,
        label: `${d.player_name} (${d.season})`
      });
    });

    chart.data.datasets = Object.keys(grouped).map((manager, i) => ({
      label: manager,
      data: grouped[manager],
      backgroundColor: colors[i % colors.length],
      borderColor: colors[i % colors.length].replace("0.7", "1"),
      pointRadius: 6,
      pointStyle: markers[i % markers.length]
    }));

    chart.update();
  }

  // Attach event listeners to filters
  filterDiv.addEventListener("change", updateChart);

  // Initial load
  updateChart();
});
