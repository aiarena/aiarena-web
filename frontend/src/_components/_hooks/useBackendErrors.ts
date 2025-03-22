import React from "react";
// I want types for this
export default function useBackendErrors(mutationName: any) {
  const [backendErrors, setBackendErrors] = React.useState({});

  const handleMutationCompleted = (data: any, errors: any) => {
    if (errors?.length || data[mutationName]?.errors?.length) {
      setBackendErrors({
        formErrors: data[mutationName]?.errors,
        graphqlErrors: errors,
      });
      return false;
    }

    if (!(mutationName in data)) {
       
      console.error(
        `Didn't find ${mutationName} in response, is the name correct?`,
      );
      setBackendErrors({ failError: true });
      return false;
    } else if (!("errors" in (data[mutationName] || {}))) {
       
      console.warn(
        `Didn't find error keys in response.${mutationName}, please include them for correct error handling.`,
      );
    }

    return true;
  };
  const handleMutationError = (error: any) => {
     
    console.error(error);
    setBackendErrors({ failError: true });
  };

  return {
    backendErrors,
    handleMutationCompleted,
    handleMutationError,
  };
}
