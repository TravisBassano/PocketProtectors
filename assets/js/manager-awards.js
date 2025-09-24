document.addEventListener("DOMContentLoaded", () => {
  // Grab JSON embedded in the HTML
  const dataEl = document.getElementById("awards-data");
  if (!dataEl) return;

  let banners;
  try {
    banners = JSON.parse(dataEl.textContent);
  } catch (e) {
    console.error("Error parsing banner JSON:", e);
    return;
  }

  const wall = document.getElementById("banner-wall");
  if (!wall) return;

  banners.forEach(banner => {
    const div = document.createElement("div");
    div.className = "banner";
    if (banner.style) div.classList.add(`banner--${banner.style}`);

    div.innerHTML = `
      <div class="banner-content">
        <div class="banner-title">${banner.title}</div>
        <div class="banner-year">${banner.year}</div>
        ${banner.style ? `<div class="star star--${banner.style}"></div>` : ""}
      </div>
    `;

    wall.appendChild(div);
  });
});
