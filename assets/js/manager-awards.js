document.addEventListener("DOMContentLoaded", () => {

  const wall = document.getElementById("banner-wall");
  if (!wall) return;

  const awall = document.getElementById("accolades-wall");
  if (!awall) return;

  const allAwards = JSON.parse(document.getElementById("awards-data").textContent);
  if (!allAwards) return;

  const allAccolades = JSON.parse(document.getElementById("accolades-data").textContent);
  if (!allAccolades) return;

  const manager = wall.dataset.manager.trim();

  const banners = allAwards[manager];
  banners.forEach(banner => {
    const div = document.createElement("div");
    div.className = "banner";
    if (banner.style) div.classList.add(`banner--${banner.style}`);

    div.innerHTML = `
      <div class="banner-content">
        <div class="banner-title">${banner.title}</div>
        <div class="banner-year">${banner.year}</div>
        ${banner.style ? `<div class="star star--${banner.style}"></div>` : `<div class="star"></div>`}
      </div>
    `;

    wall.appendChild(div);
  });

  const accolades = allAccolades[manager];
  accolades.forEach(accolade => {
    const div = document.createElement("div");
    div.className = "accolade";
    if (accolade.style) div.classList.add(`${accolade.style}`);

    div.innerHTML = `
        <div class="accolade-title">${accolade.title}</div>
        <div class="accolade-value">${accolade.value}</div>
      </div>
    `;

    awall.appendChild(div);
  });
});
