import React, { createContext, useState } from "react";
import type { ConnectionKey, ConnectionIDMap } from "./RelayConnectionIDKeys";

type RelayConnectionIDContextType = {
  getConnectionID: (key: ConnectionKey) => string;
  setConnectionID: (key: ConnectionKey, id: string) => void;
};

const RelayConnectionIDContext = createContext<
  RelayConnectionIDContextType | undefined
>(undefined);

export { RelayConnectionIDContext };
export const RelayConnectionIDProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [connectionIDs, setConnectionIDs] = useState<ConnectionIDMap>({});

  const getConnectionID = (key: ConnectionKey) => connectionIDs[key] ?? "";

  const setConnectionID = (key: ConnectionKey, id: string) => {
    setConnectionIDs((prev) => ({ ...prev, [key]: id }));
  };

  return (
    <RelayConnectionIDContext.Provider
      value={{ getConnectionID, setConnectionID }}
    >
      {children}
    </RelayConnectionIDContext.Provider>
  );
};
