import { useLazyLoadQuery, graphql } from "react-relay";
import { useViewerQuery } from "./__generated__/useViewerQuery.graphql";

export interface User {
  id: string;
  username: string;
  patreonLevel?: string;
  dateJoined?: string;
  avatarUrl?: string;
}

export interface Viewer {
  user: User;
  apiToken: string;
  email?: string;
  activeBotsLimit?: number;
  requestMatchesLimit?: number;
  requestMatchesCountLeft?: number;
}

export const useViewer = (): Viewer | null => {
  const data = useLazyLoadQuery<useViewerQuery>(
    graphql`
      query useViewerQuery {
        viewer {
          user {
            id
            username
            patreonLevel
            dateJoined
            avatarUrl
          }
          apiToken
          email
          activeBotsLimit
          requestMatchesLimit
          requestMatchesCountLeft
        }
      }
    `,
    {},
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
