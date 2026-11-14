import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import useNow from "./useNow";

export default function useUnsavedSince(isUnsaved: boolean) {
  const [baseline, setBaseline] = useState<number | null>(null);
  const prevRef = useRef<boolean>(isUnsaved);

  useEffect(() => {
    if (!prevRef.current && isUnsaved) {
      setBaseline(Date.now());
    }
    prevRef.current = isUnsaved;
  }, [isUnsaved]);

  const now = useNow(isUnsaved);

  const seconds = useMemo(() => {
    if (!isUnsaved || !baseline) return 0;
    return Math.max(0, Math.floor((now - baseline) / 1000));
  }, [isUnsaved, baseline, now]);

  const resetBaseline = useCallback(() => setBaseline(Date.now()), []);

  return { seconds, baseline, resetBaseline };
}
