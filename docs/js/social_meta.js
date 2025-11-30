// social_meta.js - dynamically adds Open Graph meta tags
function addMeta(name, content) {
    let meta = document.createElement('meta');
    meta.setAttribute('property', name);
    meta.setAttribute('content', content);
    document.getElementsByTagName('head')[0].appendChild(meta);
}

addMeta('og:title', 'My Project Name');
addMeta('og:description', 'A short description of my project');
addMeta('og:image', 'https://<your-project>.readthedocs.io/en/latest/images/Preview.png');
addMeta('og:type', 'website');
addMeta('og:url', 'https://<your-project>.readthedocs.io/en/latest/');