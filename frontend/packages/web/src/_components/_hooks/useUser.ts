import { useLazyLoadQuery, graphql } from 'react-relay';

export const useUser = () => {
  const data = useLazyLoadQuery(
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
