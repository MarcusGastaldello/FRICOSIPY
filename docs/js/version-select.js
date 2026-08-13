function populateDropdown(versions, currentSlug) {
  const select = document.getElementById("rtd-header-version-select");
  if (!select) return;

  // Don't overwrite if we already built the menu
  if (select.children.length > 1 && select.options[0].value !== "#") return;

  select.innerHTML = ""; // Clear placeholder

  versions.forEach((v) => {
    const opt = document.createElement("option");
    // Get URL from RTD Addon object or construct path
    const url = v.urls ? v.urls.documentation : `/${window.READTHEDOCS_DATA?.language || 'en'}/${v.slug || v}/`;
    const slug = v.slug || v;

    opt.value = url;
    opt.textContent = slug + " ▾";
    opt.style.color = "#333";
    opt.style.backgroundColor = "#fff";

    if (slug === currentSlug) {
      opt.selected = true;
    }
    select.appendChild(opt);
  });
}

function initSelector() {
  const currentSlug = window.READTHEDOCS_DATA?.version || "latest";

  // 1. Try Read the Docs Addons Object
  if (window.readthedocs?.addons?.addons?.versions?.active) {
    populateDropdown(window.readthedocs.addons.addons.versions.active, currentSlug);
    return;
  }

  // 2. Try classic RTD data object
  if (window.READTHEDOCS_DATA) {
    const project = window.READTHEDOCS_DATA.project;
    fetch(`https://readthedocs.org/api/v2/version/?project__slug=${project}&active=true`)
      .then((res) => res.json())
      .then((data) => {
        if (data.results && data.results.length > 0) {
          populateDropdown(data.results, currentSlug);
        } else {
          // If RTD API returns only 1 version, keep a clean fallback display
          populateDropdown([{ slug: currentSlug }], currentSlug);
        }
      })
      .catch(() => populateDropdown([{ slug: currentSlug }], currentSlug));
  }
}

// Listen for RTD Event
document.addEventListener("readthedocs-addons-data-ready", function (event) {
  const addons = event.detail;
  if (addons?.addons?.versions?.active) {
    populateDropdown(addons.addons.versions.active, addons.version?.slug);
  }
});

// Run on initial load AND every time page navigation completes
document.addEventListener("DOMContentLoaded", initSelector);
window.addEventListener("load", initSelector);
