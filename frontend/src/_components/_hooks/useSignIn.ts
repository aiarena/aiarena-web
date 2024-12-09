import { useMutation, graphql } from 'react-relay';
import { useState } from 'react';
import { useSignInMutation } from './__generated__/useSignInMutation.graphql';



type SignInFunction = (username: string, password: string, onSuccess?: () => void) => void;

export const useSignIn = (): [SignInFunction, boolean, string | null] => {
  const [commit, isInFlight] = useMutation<useSignInMutation>(
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

  const [error, setError] = useState<string | null>(null);

  const signIn: SignInFunction = (username, password, onSuccess) => {
    commit({
      variables: {
        input: { username, password },
      },
      onCompleted: (response) => {
        const errors = response?.passwordSignIn?.errors;
        if (errors && errors.length > 0) {
          // Safely access the first error message
          const firstErrorMessage = errors[0]?.messages?.[0] ?? 'An unknown error occurred.';
          setError(firstErrorMessage);
        } else {
              setError(null); // Clear error if no issues
              if (onSuccess) {
                onSuccess(); // Call the success callback
              }
            }
      },

      onError: (err) => {
        setError('Something went wrong. Please try again.'); // Handle unexpected errors
      }
    });
  };

  return [signIn, isInFlight, error];
};
