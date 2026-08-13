document.addEventListener("DOMContentLoaded", function () {
    // Wait for Read the Docs to inject the flyout
    const observer = new MutationObserver((mutations, obs) => {
        const flyout = document.querySelector("readthedocs-flyout");
        const sidebarHeader = document.querySelector(".wy-side-nav-search");

        if (flyout && sidebarHeader) {
            // Physically move the flyout element inside the sidebar header
            sidebarHeader.appendChild(flyout);

            // Override its fixed positioning to inline/relative layout
            flyout.style.position = "static";
            flyout.style.display = "block";
            flyout.style.margin = "10px 0";

            // Inject blue color styling directly into the shadow root if present
            if (flyout.shadowRoot) {
                const style = document.createElement('style');
                style.textContent = `
                    * { color: #55a5d9 !important; }
                    a, button, span { color: #55a5d9 !important; fill: #55a5d9 !important; }
                `;
                flyout.shadowRoot.appendChild(style);
            }

            obs.disconnect(); // Stop observing once moved
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
