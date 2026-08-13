function initVersionSelector(versions, currentSlug) {
  const select = document.getElementById("rtd-header-version-select");
  if (!select || !versions || versions.length === 0) return;

  select.innerHTML = ""; // Clear fallback option

  versions.forEach((v) => {
    const opt = document.createElement("option");
    // Handle both RTD Addons object format and RTD API format
    const url = v.urls ? v.urls.documentation : `/${window.READTHEDOCS_DATA?.language || 'en'}/${v.slug}/`;
    const slug = v.slug;

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

function setup() {
  // 1. Check if RTD Addons data is already globally available
  if (window.readthedocs && window.readthedocs.addons) {
    const addons = window.readthedocs.addons;
    initVersionSelector(addons.addons?.versions?.active, addons.version?.slug);
    return;
  }

  // 2. Listen for the Addon event if it hasn't fired yet
  document.addEventListener("readthedocs-addons-data-ready", function (event) {
    const addons = event.detail;
    initVersionSelector(addons.addons?.versions?.active, addons.version?.slug);
  });

  // 3. Fallback to classic RTD object + API fetch if Addons are slow/disabled
  if (window.READTHEDOCS_DATA) {
    const project = window.READTHEDOCS_DATA.project;
    const currentVersion = window.READTHEDOCS_DATA.version;
    
    fetch(`https://readthedocs.org/api/v2/version/?project__slug=${project}&active=true`)
      .then((res) => res.json())
      .then((data) => {
        if (data.results) {
          initVersionSelector(data.results, currentVersion);
        }
      })
      .catch(() => {});
  }
}

// Run immediately if DOM is ready, otherwise wait for load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", setup);
} else {
  setup();
}
