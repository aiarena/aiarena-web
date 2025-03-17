"use client";

import { RelayEnvironmentProvider } from "react-relay";
import RelayEnvironment from "@/_lib/RelayEnvironment";
import { LoginProvider } from "@/_components/providers/LoginProvider";
import { ViewerProvider } from "@/_components/providers/ViewerProvider";
import ErrorBoundary from "./ErrorBoundary";

export default function ClientWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      <ErrorBoundary>
        <RelayEnvironmentProvider environment={RelayEnvironment}>
          <LoginProvider>
            <ViewerProvider>{children}</ViewerProvider>
          </LoginProvider>
        </RelayEnvironmentProvider>
      </ErrorBoundary>
    </div>
  );
}
