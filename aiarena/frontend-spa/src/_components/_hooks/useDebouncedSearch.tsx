import { useEffect, useRef } from "react";

export function useDebouncedQuery(
  searchValue: string,
  orderBy: string,
  delay: number,
  onDebounced: (value: string, orderBy: string) => void,
  onLoadingChange?: (isLoading: boolean) => void
): void {
  const lastSearchRef = useRef(searchValue);
  const lastOrderByRef = useRef(orderBy);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const hasChanged =
      lastSearchRef.current !== searchValue ||
      lastOrderByRef.current !== orderBy;

    if (!hasChanged) return;

    onLoadingChange?.(true);

    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = setTimeout(() => {
      lastSearchRef.current = searchValue;
      lastOrderByRef.current = orderBy;

      onDebounced(searchValue, orderBy);
      onLoadingChange?.(false);
    }, delay);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [searchValue, orderBy, delay, onDebounced, onLoadingChange]);
}
