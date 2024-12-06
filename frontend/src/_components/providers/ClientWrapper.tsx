'use client';

import { RelayEnvironmentProvider } from 'react-relay';
import RelayEnvironment from '@/_lib/RelayEnvironment';
import { LoginProvider } from '@/_components/providers/LoginProvider';
import { UserProvider } from '@/_components/providers/UserProvider';

export default function ClientWrapper({ children }: { children: React.ReactNode }) {
  return (
    <RelayEnvironmentProvider environment={RelayEnvironment}>
      <LoginProvider>
        <UserProvider>{children}</UserProvider>
      </LoginProvider>
    </RelayEnvironmentProvider>
  );
}