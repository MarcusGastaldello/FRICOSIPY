document.addEventListener("DOMContentLoaded", function () {
    const observer = new MutationObserver((mutations, obs) => {
        const flyout = document.querySelector("readthedocs-flyout");
        const sidebarHeader = document.querySelector(".wy-side-nav-search");

        if (flyout && sidebarHeader) {
            // 1. Physically move the element under the logo in the sidebar DOM
            sidebarHeader.appendChild(flyout);

            // 2. Clear outer fixed-position styles
            flyout.style.setProperty("position", "relative", "important");
            flyout.style.setProperty("display", "block", "important");
            flyout.style.setProperty("margin-top", "15px", "important");
            flyout.style.setProperty("bottom", "auto", "important");
            flyout.style.setProperty("right", "auto", "important");

            // 3. Inject CSS directly into the Shadow DOM to kill internal fixed positioning
            if (flyout.shadowRoot) {
                const style = document.createElement('style');
                style.textContent = `
                    /* Target internal container wrapper inside Shadow DOM */
                    :host, 
                    .floating, 
                    .container, 
                    div[class*="container"], 
                    header, 
                    main {
                        position: relative !important;
                        bottom: auto !important;
                        right: auto !important;
                        left: auto !important;
                        top: auto !important;
                        margin: 0 !important;
                        box-shadow: none !important;
                    }
                    * { 
                        color: #55a5d9 !important; 
                    }
                    a, button, span { 
                        color: #55a5d9 !important; 
                        fill: #55a5d9 !important; 
                    }
                `;
                flyout.shadowRoot.appendChild(style);
            }

            obs.disconnect(); // Stop checking once moved
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
