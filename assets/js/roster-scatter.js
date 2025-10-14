document.addEventListener("DOMContentLoaded", () => {
  const rawData = document.getElementById("manager-data").textContent;
  const data = JSON.parse(rawData);

  const ctx = document.getElementById("pointsChart");

  const managers = [...new Set(data.map(d => d.manager))];
  const positions = [...new Set(data.map(d => d.position))];

  // 🎨 Manager colors and shapes
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

  const datasets = managers.map((mgr, i) => ({
    label: mgr,
    data: data
      .filter(d => d.manager === mgr)
      .map(d => ({
        x: positions.indexOf(d.position),
        y: d.points,
        position: d.position,
        season: d.season
      })),
    backgroundColor: colors[i % colors.length],
    borderColor: colors[i % colors.length],
    pointStyle: pointStyles[i % pointStyles.length],
    pointRadius: 8
  }));

  new Chart(ctx, {
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
          position: "right",
          labels: { usePointStyle: true, boxWidth: 10 }
        },
        tooltip: {
          callbacks: {
            label: ctx => {
              const d = ctx.raw;
              return `${ctx.dataset.label}: ${d.position}, ${d.points} pts (${d.season})`;
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
});
