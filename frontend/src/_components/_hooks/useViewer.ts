import { useLazyLoadQuery, graphql } from 'react-relay';
import { useViewerQuery } from './__generated__/useViewerQuery.graphql';
import { useMemo } from 'react';


export interface User {
  id: string;
  username: string;
  email: string;
  patreonLevel?: string;
  dateJoined?: string;
  activeBotsLimit?: number;
  requestMatchesLimit?: number;
  requestMatchesCountLeft?: number;
  avatarUrl?: string;
}


export interface Viewer {
  user: User;
  apiToken: string;
}


export const useViewer = (): Viewer | null => {

  const data = useLazyLoadQuery<useViewerQuery>(
    graphql`
      query useViewerQuery {            
        viewer {
        user {
        id
          username
          email
          patreonLevel
          dateJoined
          activeBotsLimit
          requestMatchesLimit
          requestMatchesCountLeft
          avatarUrl
        }
          apiToken
        }
      }
    `,
    {}
  );
  // console.log("Console.log DATA: ", data)
  // Always call `useMemo` and safely handle null or undefined data
  // const user = useMemo(() => {
  //   if (!data?.viewer) return null;

  //   return {

  //     id: data.viewer.user?.id,
  //     username: data.viewer.user?.username,
  //     email: data.viewer.user?.email,
  //     patreonLevel: data.viewer.user?.patreonLevel ?? undefined,
  //     dateJoined: data.viewer.user?.dateJoined ?? undefined,
  //     activeBotsLimit: data.viewer.user?.activeBotsLimit ?? undefined,
  //     requestMatchesLimit: data.viewer.user?.requestMatchesLimit ?? undefined,
  //     requestMatchesCountLeft: data.viewer.user?.requestMatchesCountLeft ?? undefined,
  //     avatarUrl: data.viewer.user?.avatarUrl ?? undefined,
  //     apiToken: data.viewer.apiToken ?? undefined,
  //   };
  // }, [data]);

  return data.viewer as Viewer;
};

