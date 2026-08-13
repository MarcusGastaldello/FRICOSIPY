document.addEventListener("DOMContentLoaded", function () {
  const select = document.getElementById("rtd-header-version-select");
  if (!select) return;

  // Listen for Read the Docs Addon data
  document.addEventListener("readthedocs-addons-data-ready", function (event) {
    const addons = event.detail;
    const versions = addons.addons?.versions?.active || [];

    select.innerHTML = ""; // Clear loading state

    versions.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v.urls.documentation;
      opt.textContent = v.slug + " ▾";
      opt.style.color = "#333"; // Keep dropdown list text dark

      if (v.slug === addons.version.slug) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });
  });
});
