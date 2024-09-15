import { useMutation, graphql } from 'react-relay';

export const useSignIn = () => {
  const [commit, isInFlight] = useMutation(
    graphql`
      mutation useSignInMutation($input: PasswordSignInInput!) {
        passwordSignIn(input: $input) {
          errors {
            field
            messages
          }
        }
      }
    `
  );

  const signIn = (username, password) => {
    commit({
      variables: {
        input: { username, password },
      },
    });
  };

  return [signIn, isInFlight];
};
