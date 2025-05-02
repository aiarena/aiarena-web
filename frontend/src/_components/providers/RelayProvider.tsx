"use client";

import { ReactNode } from "react";

import { RelayEnvironmentProvider } from "react-relay";
import { Environment } from "relay-runtime"; // Ensure we have the Environment type
import { useEnvironment } from "@/_lib/relay/RelayEnvironment";
interface RelayProviderProps {
  children: ReactNode;
}

export default function RelayProvider({ children }: RelayProviderProps) {
  const initialRecords = [] as any;
  // Getting the Relay environment from your custom hook
  const environment: Environment = useEnvironment(initialRecords);

  return (
    <div>
      <RelayEnvironmentProvider environment={environment}>
        {children}
      </RelayEnvironmentProvider>
    </div>
  );
}
