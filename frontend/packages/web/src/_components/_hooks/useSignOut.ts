import { useMutation, graphql } from 'react-relay';

export const useSignOut = () => {
  const [commit, isInFlight] = useMutation(
    graphql`
      mutation useSignOutMutation {
        signOut {
          errors {
            field
            messages
          }
        }
      }
    `
  );

  const signOut = () => {
    commit();
  };

  return [signOut, isInFlight];
};
