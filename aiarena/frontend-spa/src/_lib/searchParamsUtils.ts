import { SortingState } from "@tanstack/react-table";

export const cleanStr = (v: unknown) =>
    typeof v === "string" && v.trim() !== "" ? v : undefined;

export const toNum = (v: string | null) => {
    if (!v) return undefined;
    const n = Number(v);
    return Number.isFinite(n) ? n : undefined;
};

export const toBool = (v: string | null, fallback: boolean) =>
    v == null ? fallback : v === "1";

export function setOrDelete(sp: URLSearchParams, key: string, value?: string) {
    if (!value) sp.delete(key);
    else sp.set(key, value);
}

export function setPair(
    searchParam: URLSearchParams,
    idKey: string,
    idVal?: string,
    nameKey?: string,
    nameVal?: string,
) {
    if (!idVal) {
        searchParam.delete(idKey);
        if (nameKey) searchParam.delete(nameKey);
        return;
    }
    searchParam.set(idKey, idVal);
    if (nameKey) setOrDelete(searchParam, nameKey, nameVal);
}

export function encodeSortingToSearchParams(
    sorting: SortingState,
    prev: URLSearchParams,
    SORT_KEY: string,
) {
    const searchParam = new URLSearchParams(prev);

    const s = sorting?.[0];
    if (!s?.id) {
        searchParam.delete(SORT_KEY);
        return searchParam;
    }

    searchParam.set(SORT_KEY, `${s.desc ? "-" : ""}${s.id}`);
    return searchParam;
}

export function decodeSortingFromSearchParams(
    searchParam: URLSearchParams,
    allowedIds: ReadonlySet<string>,
    SORT_KEY: string,
): SortingState {
    const raw = searchParam.get(SORT_KEY);
    if (!raw) return [];

    const desc = raw.startsWith("-");
    const id = desc ? raw.slice(1) : raw;

    if (!allowedIds.has(id)) return [];
    return [{ id, desc }];
}
