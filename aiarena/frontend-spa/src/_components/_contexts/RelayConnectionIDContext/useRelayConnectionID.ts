import { useContext } from "react";
import { RelayConnectionIDContext } from "./RelayConnectionIDContext";

export const useRelayConnectionID = () => {
  const context = useContext(RelayConnectionIDContext);
  if (!context) {
    throw new Error(
      "useRelayConnectionID must be used within a RelayConnectionIDProvider",
    );
  }
  return context;
};
