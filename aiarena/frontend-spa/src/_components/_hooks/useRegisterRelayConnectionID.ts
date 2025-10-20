import { useEffect, useRef } from "react";
import { useRelayConnectionID } from "../_contexts/RelayConnectionIDContext/useRelayConnectionID";
import { ConnectionKey } from "../_contexts/RelayConnectionIDContext/RelayConnectionIDKeys";

export function useRegisterConnectionID(
  key: ConnectionKey,
  id: string | undefined | null,
) {
  const { setConnectionID } = useRelayConnectionID();
  const lastID = useRef<string | null>(null);

  useEffect(() => {
    if (id && lastID.current !== id) {
      lastID.current = id;
      setConnectionID(key, id);
    }
  }, [id, key, setConnectionID]);
}
