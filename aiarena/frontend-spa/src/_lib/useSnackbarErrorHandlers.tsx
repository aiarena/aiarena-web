import { useSnackbar } from "notistack";
import React from "react";

import useBackendErrors, {
  getMessageList,
  GraphqlError,
  OnCompletedResponse,
} from "./useBackendErrors";

export default function useSnackbarErrorHandlers(
  mutationName: string,
  successMessage: string,
) {
  const { enqueueSnackbar } = useSnackbar();
  const {
    backendErrors,
    onCompleted: onMutationCompleted,
    onError: onMutationError,
  } = useBackendErrors(mutationName);

  React.useEffect(() => {
    const messages = getMessageList(backendErrors);
    if (!messages.length) {
      return;
    }

    enqueueSnackbar(<span>{messages.join("; ")}</span>, { variant: "error" });
  }, [enqueueSnackbar, backendErrors]);

  const handleMutationCompleted = (
    response: OnCompletedResponse,
    errors: GraphqlError[] | null,
  ) => {
    const success = onMutationCompleted(response, errors);

    if (!success || !successMessage) {
      return;
    }

    enqueueSnackbar(<span>{successMessage}</span>, {
      variant: "default",
    });
  };

  return {
    onCompleted: handleMutationCompleted,
    onError: onMutationError,
  };
}
