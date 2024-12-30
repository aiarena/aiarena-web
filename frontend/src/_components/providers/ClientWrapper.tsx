"use client";

import { RelayEnvironmentProvider } from "react-relay";
import RelayEnvironment from "@/_lib/RelayEnvironment";
import { LoginProvider } from "@/_components/providers/LoginProvider";
import { UserProvider } from "@/_components/providers/UserProvider";
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
            <UserProvider>{children}</UserProvider>
          </LoginProvider>
        </RelayEnvironmentProvider>
      </ErrorBoundary>
    </div>
  );
}
