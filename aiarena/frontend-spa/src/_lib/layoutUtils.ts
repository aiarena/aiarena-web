export function scrollToHashWithOffset(offset = -40) {
    if (!window.location.hash) return;

    const id = window.location.hash.slice(1);
    const el = document.getElementById(id);
    if (!el) return;

    const rect = el.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const top = rect.top + scrollTop + offset;

    window.scrollTo({
        top,
        behavior: "smooth",
    });
}