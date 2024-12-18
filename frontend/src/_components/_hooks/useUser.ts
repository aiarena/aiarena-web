import { useLazyLoadQuery, graphql } from 'react-relay';
import { useUserQuery } from './__generated__/useUserQuery.graphql';
import { useMemo } from 'react';

export interface User {
  id: string;
  username: string;
  email: string;
  patreonLevel?: string;
  dateJoined?: string;
}

export const useUser = (): User | null => {
  const data = useLazyLoadQuery<useUserQuery>(
    graphql`
      query useUserQuery {
        viewer {
          id
          username
          email
          patreonLevel
          dateJoined
        }
      }
    `,
    {}
  );

  // Always call `useMemo` and safely handle null or undefined data
  const user = useMemo(() => {
    if (!data?.viewer) return null;

    return {
      id: data.viewer.id,
      username: data.viewer.username,
      email: data.viewer.email,
      patreonLevel: data.viewer.patreonLevel ?? undefined,
      dateJoined: data.viewer.dateJoined ?? undefined,
    };
  }, [data]);

  return user;
};
