import { useMutation, graphql } from 'react-relay';
import { useState } from 'react';

export const useSignOut = (): [() => void, boolean, string | null] => {
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

  const [error, setError] = useState<string | null>(null);

  const signOut = () => {
    commit({
      variables: {}, // No variables needed for sign out mutation
      onCompleted: (response) => {
        const errors = response?.signOut?.errors;
        if (errors && errors.length > 0) {
          setError(errors[0].messages[0]); // Handle and display error
        } else {
          setError(null); // Clear error on success
        }
      },
      onError: (err) => {
        setError('Something went wrong during sign out. Please try again.');
      }
    });
  };

  return [signOut, isInFlight, error];
};
