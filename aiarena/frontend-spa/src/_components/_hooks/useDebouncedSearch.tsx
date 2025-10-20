import { useEffect, useRef } from "react";

export function useDebouncedSearch(
  searchValue: string,
  delay: number,
  onDebounced: (value: string) => void,
  onLoadingChange?: (isLoading: boolean) => void,
): void {
  const lastSearchRef = useRef(searchValue);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const hasChanged = lastSearchRef.current !== searchValue;

    if (!hasChanged) return;

    onLoadingChange?.(true);

    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = setTimeout(() => {
      lastSearchRef.current = searchValue;

      onDebounced(searchValue);
      onLoadingChange?.(false);
    }, delay);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [searchValue, delay, onDebounced, onLoadingChange]);
}
