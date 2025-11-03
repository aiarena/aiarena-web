import { useCallback, useEffect, useMemo, useRef, useState } from "react";

export default function useUnsavedSince(isUnsaved: boolean) {
  const [baseline, setBaseline] = useState<number | null>(null);
  const [now, setNow] = useState<number>(() => Date.now());
  const prevRef = useRef<boolean>(isUnsaved);

  useEffect(() => {
    if (!prevRef.current && isUnsaved) {
      setBaseline(Date.now());
    }
    prevRef.current = isUnsaved;
  }, [isUnsaved]);

  useEffect(() => {
    if (!isUnsaved) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [isUnsaved]);

  const seconds = useMemo(() => {
    if (!isUnsaved || !baseline) return 0;
    return Math.max(0, Math.floor((now - baseline) / 1000));
  }, [isUnsaved, baseline, now]);

  const resetBaseline = useCallback(() => setBaseline(Date.now()), []);

  return { seconds, baseline, resetBaseline };
}
