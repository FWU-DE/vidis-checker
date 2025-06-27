LOCAL_STORAGE_CODE = """
() => {
    const items = {};
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        items[key] = localStorage.getItem(key);
    }
    return items;
}
""".strip()

SESSION_STORAGE_CODE = """
() => {
    const items = {};
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        items[key] = sessionStorage.getItem(key);
    }
    return items;
}
""".strip()

RESOURCES_CODE = """
() => {
    const resources = [];
    const elements = document.querySelectorAll('img, iframe, script, object, embed');
    elements.forEach(el => {
        let src = el.src || el.data;
        if (src) {
            resources.push({
                type: el.tagName.toLowerCase(),
                url: src,
                width: el.width || null,
                height: el.height || null,
                id: el.id || null,
                className: el.className || null
            });
        }
    });
    return resources;
}
""".strip()

SCROLL_TO_BOTTOM_CODE = """
window.scrollTo(0, document.body.scrollHeight);
""".strip()
