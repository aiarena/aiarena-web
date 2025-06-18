import { useEffect } from "react";

export default function SuspenseGetLoading({
  setLoading,
}: {
  setLoading: (v: boolean) => void;
}) {
  useEffect(() => {
    setLoading(true);
    return () => setLoading(false);
  }, [setLoading]);

  return <></>;
}
