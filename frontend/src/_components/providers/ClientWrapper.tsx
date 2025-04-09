"use client";

// import { RelayEnvironmentProvider } from "react-relay";
import { LoginProvider } from "@/_components/providers/LoginProvider";
import { ViewerProvider } from "@/_components/providers/ViewerProvider";
import ErrorBoundary from "./ErrorBoundary";

import RelayProvider from "./RelayProvider";

export default function ClientWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      <ErrorBoundary>
        {/* OLD RELAY ENVIORNMENT - SHARED STATE ON SERVER */}
        {/* <RelayEnvironmentProvider environment={RelayEnvironment}> */}

        {/* New Relay enviornment - Unique env per request on server */}
        <RelayProvider>
          <LoginProvider>
            <ViewerProvider>{children}</ViewerProvider>
          </LoginProvider>
        </RelayProvider>
        {/* </RelayEnvironmentProvider> */}
      </ErrorBoundary>
    </div>
  );
}
