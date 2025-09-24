document.addEventListener("DOMContentLoaded", () => {
  const allAwards = JSON.parse(document.getElementById("awards-data").textContent);
  const manager = "{{ page.manager }}".trim();
  if (!allAwards) return;

  const banners = allAwards[manager];

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
        ${banner.style ? `<div class="star star--${banner.style}"></div>` : `<div class="star"></div>`}
      </div>
    `;

    wall.appendChild(div);
  });
});
