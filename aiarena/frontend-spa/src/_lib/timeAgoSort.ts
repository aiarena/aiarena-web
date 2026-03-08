export default function timeAgoShort(
    from: Date | number | string,
    to: Date | number = Date.now(),
): string {
    const start = new Date(from).getTime();
    const end = new Date(to).getTime();
    let ms = Math.abs(end - start);

    const MS = {
        w: 7 * 24 * 60 * 60 * 1000,
        d: 24 * 60 * 60 * 1000,
        h: 60 * 60 * 1000,
        m: 60 * 1000,
        s: 1000,
    };

    const parts: Array<[number, string]> = [];

    const w = Math.floor(ms / MS.w);
    if (w) parts.push([w, "w"]);
    ms %= MS.w;
    const d = Math.floor(ms / MS.d);
    if (d) parts.push([d, "d"]);
    ms %= MS.d;
    const h = Math.floor(ms / MS.h);
    if (h) parts.push([h, "h"]);
    ms %= MS.h;
    const m = Math.floor(ms / MS.m);
    if (m) parts.push([m, "m"]);
    ms %= MS.m;
    const s = Math.floor(ms / MS.s);
    if (s) parts.push([s, "s"]);

    if (parts.length === 0) return "0s";

    if (parts[0][1] === "w") {
        // Only return the week if the string starts with a week count
        return parts
            .slice(0, 1)
            .map(([v, u]) => `${v}${u}`)
            .join(" ");
    }

    // else return two largest units - i.e. day, hour /or/ hour, minute
    return parts
        .slice(0, 2)
        .map(([v, u]) => `${v}${u}`)
        .join(" ");
}