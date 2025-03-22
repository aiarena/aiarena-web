import { useMutation, graphql } from "react-relay";
import { useState } from "react";

import { useSignOutMutation } from "./__generated__/useSignOutMutation.graphql";

export const useSignOut = (): [() => void, boolean, string | null] => {
  const [commit, isInFlight] = useMutation<useSignOutMutation>(graphql`
    mutation useSignOutMutation {
      signOut {
        errors {
          field
          messages
        }
      }
    }
  `);

  const [error, setError] = useState<string | null>(null);

  const signOut = () => {
    commit({
      variables: {}, // No variables needed for sign out mutation
      onCompleted: (response: useSignOutMutation["response"]) => {
        const errors = response?.signOut?.errors;
        if (errors && errors.length > 0) {
          const firstErrorMessage =
            errors[0]?.messages?.[0] ?? "An unknown error occurred.";
          setError(firstErrorMessage); // Handle and display the first error message
        } else {
          setError(null); // Clear error on success
        }
      },
      onError: () => {
        setError("Something went wrong during sign out. Please try again.");
      },
    });
  };

  return [signOut, isInFlight, error];
};
