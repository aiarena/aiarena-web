import React from "react";

interface FormError {
  readonly field: string;
  readonly messages: readonly string[];
}

export interface GraphqlError {
  readonly message: string;
}

export interface MutationData {
  [key: string]: unknown;
  readonly errors?: readonly (FormError | null | undefined)[] | null | undefined;
}

export interface BackendErrors {
  formErrors?: readonly (FormError | null | undefined)[] | null;
  graphqlErrors?: readonly GraphqlError[] | null;
  failError?: boolean;
}

export interface OnCompletedResponse {
  [key: string]: MutationData | undefined | null;

}

export default function useBackendErrors(mutationName: string) {
  const [backendErrors, setBackendErrors] = React.useState<BackendErrors>({});
  const successRef = React.useRef(false);

  const handleMutationCompleted = (
    response: OnCompletedResponse,
    errors: GraphqlError[] | null,
  ) => {
    const raw = response[mutationName]?.errors;
    const formErrors = raw?.filter((e): e is FormError => !!e) ?? [];

    if (errors?.length || response[mutationName]?.errors?.length) {
      setBackendErrors({
        formErrors: formErrors,
        graphqlErrors: errors,
      });
      return false;
    }

    if (!(mutationName in response)) {
      console.error(
        `Didn't find ${mutationName} in response, is the name correct?`,
      );
      setBackendErrors({ failError: true });
      return false;
    } else if (!("errors" in (response[mutationName] || {}))) {
      console.warn(
        `Didn't find error keys in response.${mutationName}, please include them for correct error handling.`,
      );
    }

    return true;
  };
  const handleMutationError = (error: Error) => {
    console.error(error);
    setBackendErrors({ failError: true });
  };

  return {
    success: successRef.current,
    backendErrors,
    onCompleted: handleMutationCompleted,
    onError: handleMutationError,
  };
}

export function getMessageList({
  formErrors,
  graphqlErrors,
  failError,
}: BackendErrors) {
  const formMessages =
    formErrors?.filter((e): e is FormError => !!e)?.map((error) => {
      const messages = error.messages.join("; ");

      if (error.field === "__all__") {
        return messages;
      }

      return `${error.field} - ${messages}`;
    }) || [];
  const graphqlMessages = graphqlErrors?.map((error) => error.message) || [];
  const failMessages = failError ? [`Something went wrong :(`] : [];

  return [...formMessages, ...graphqlMessages, ...failMessages];
}
