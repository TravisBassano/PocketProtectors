document.addEventListener("DOMContentLoaded", () => {
  const rawData = document.getElementById("rosters-data").textContent;
  const data = JSON.parse(rawData);
  const ctx = document.getElementById("pointsChart");

  const managers = [...new Set(data.map(d => d.manager))];
  const positions = [...new Set(data.map(d => d.position))];
  const seasons = [...new Set(data.map(d => d.season))].sort();

  const colors = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf", "#17a2b8", "#ff6666"
  ];
  const pointStyles = [
    "circle", "triangle", "rect", "rectRounded",
    "star", "cross", "crossRot", "dash",
    "line", "rectRot", "triangle", "circle"
  ];

  // --- Create season filter pills dynamically ---
  const filtersContainer = document.getElementById("season-filters");
  seasons.forEach(season => {
    const input = document.createElement("input");
    input.type = "checkbox";
    input.id = `season-${season}`;
    input.value = season;
    input.checked = true;

    const label = document.createElement("label");
    label.setAttribute("for", `season-${season}`);
    label.textContent = season;

    filtersContainer.appendChild(input);
    filtersContainer.appendChild(label);

    input.addEventListener("change", updateChart);
  });

  let chart;

  function buildDatasets(selectedSeasons) {
    return managers.map((mgr, i) => {
      const mgrData = data.filter(
        d => d.manager === mgr && selectedSeasons.includes(d.season)
      );

      // Aggregate (sum) points per position
      const aggregated = {};
      mgrData.forEach(d => {
        aggregated[d.position] = (aggregated[d.position] || 0) + d.points;
      });

      return {
         label: mgr,
         data: Object.entries(aggregated).map(([pos, pts]) => {
            const baseX = positions.indexOf(pos);

            // --- Deterministic jitter based on manager name ---
            const hash = Array.from(mgr).reduce((acc, c) => acc + c.charCodeAt(0), 0);
            const jitter = ((hash % 100) / 100 - 0.5) * 0.3; // range roughly [-0.15, +0.15]

            return {
               x: baseX + jitter,
               y: pts,
               position: pos
            };
         }),
         backgroundColor: colors[i % colors.length],
         borderColor: colors[i % colors.length],
         pointStyle: pointStyles[i % pointStyles.length],
         pointRadius: 8
         };
    });
  }

  function updateChart() {
    const selectedSeasons = seasons.filter(
      s => document.getElementById(`season-${s}`).checked
    );
    const datasets = buildDatasets(selectedSeasons);

    if (chart) {
      chart.data.datasets = datasets;
      chart.update();
    } else {
      chart = new Chart(ctx, {
        type: "scatter",
        data: { datasets },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: "MVKC — Seasons 2018–2024",
              font: { size: 18, weight: "bold" },
              padding: { top: 10, bottom: 20 }
            },
            subtitle: {
              display: true,
              text: "Player Position Points Comparison Across All Managers"
            },
            legend: {
              position: "top", // ✅ moved above the plot
              labels: { usePointStyle: true, boxWidth: 10 }
            },
            tooltip: {
              callbacks: {
                label: ctx => {
                  const d = ctx.raw;
                  return `${ctx.dataset.label}: ${d.position}, ${d.y} pts`;
                }
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: "Player Position" },
              ticks: {
                callback: (value, index) => positions[index] || ""
              },
              grid: { color: "rgba(200,200,200,0.3)" }
            },
            y: {
              title: { display: true, text: "Points" },
              grid: { color: "rgba(200,200,200,0.3)" }
            }
          }
        }
      });
    }
  }

  updateChart(); // Initial render
});