import { useLazyLoadQuery, graphql } from 'react-relay';
import { useUserQuery } from './__generated__/useUserQuery.graphql';

export const useUser = () => {
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
  return data.viewer;
};


