import React from 'react';

export default function useBackendErrors(mutationName) {
  const [backendErrors, setBackendErrors] = React.useState({});

  const handleMutationCompleted = (data, errors) => {
    if (errors?.length || data[mutationName]?.errors?.length) {
      setBackendErrors({
        formErrors: data[mutationName]?.errors,
        graphqlErrors: errors,
      });
      return false;
    }

    if (!(mutationName in data)) {
      // eslint-disable-next-line no-console
      console.error(
        `Didn't find ${mutationName} in response, is the name correct?`
      );
      setBackendErrors({ failError: true });
      return false;
    } else if (!("errors" in (data[mutationName] || {}))) {
      // eslint-disable-next-line no-console
      console.warn(
        `Didn't find error keys in response.${mutationName}, please include them for correct error handling.`
      );
    }

    return true;
  };
  const handleMutationError = (error) => {
    // eslint-disable-next-line no-console
    console.error(error);
    setBackendErrors({ failError: true });
  };

  return {
    backendErrors,
    handleMutationCompleted,
    handleMutationError,
  };
}