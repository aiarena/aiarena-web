import { useEffect, useRef } from "react";

export function useDebouncedSearch(
  searchValue: string,
  delay: number,
  onDebounced: (value: string) => void
) {
  const lastValueRef = useRef(searchValue);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = setTimeout(() => {
      if (lastValueRef.current !== searchValue) {
        lastValueRef.current = searchValue;
        onDebounced(searchValue);
      }
    }, delay);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [searchValue, delay, onDebounced]);
}
