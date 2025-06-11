import { useEffect, useRef } from "react";

export function useDebounced<T>(
  value: T,
  delay: number,
  onDebounced: (value: T) => void,
  onLoadingChange?: (isLoading: boolean) => void
): void {
  const lastSearchRef = useRef(value);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const hasChanged = lastSearchRef.current !== value;

    if (!hasChanged) return;

    onLoadingChange?.(true);

    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = setTimeout(() => {
      lastSearchRef.current = value;

      onDebounced(value);
      onLoadingChange?.(false);
    }, delay);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [value, delay, onDebounced, onLoadingChange]);
}
