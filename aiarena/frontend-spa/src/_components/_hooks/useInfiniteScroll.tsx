import { useCallback, useRef } from "react";

export const useInfiniteScroll = (
  fetchCallback: () => void,
  hasMore: boolean
) => {
  const observer = useRef<IntersectionObserver | null>(null);

  const loadMoreRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (observer.current) observer.current.disconnect();

      if (node && hasMore) {
        observer.current = new IntersectionObserver(([entry]) => {
          if (entry.isIntersecting) {
            fetchCallback();
          }
        });
        observer.current.observe(node);
      }
    },
    [fetchCallback, hasMore]
  );

  return { loadMoreRef };
};
