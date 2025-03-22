import React from "react";
import Alert from "@/_components/_display/Alert";

interface BackendErrorsProps {
  formErrors: {
    messages: string[];
    field: string;
  }[];
  graphqlErrors: {
    message: string;
  }[];
  failError: string | null;
}

export default function BackendErrors({
  formErrors = [],
  graphqlErrors = [],
  failError = null,
}: BackendErrorsProps) {
  const formMessages =
    formErrors?.map((error) => {
      const messages = error.messages.join("; ");

      if (error.field === "__all__") {
        return messages;
      }

      return `${error.field} - ${messages}`;
    }) || [];
  const graphqlMessages = graphqlErrors?.map((error) => error.message) || [];
  const failMessages = failError ? [`Something went wrong :(`] : [];

  const finalMessages = [...formMessages, ...graphqlMessages, ...failMessages];

  if (!finalMessages.length) {
    return null;
  }

  const message = finalMessages.join(", ");

  return <Alert message={message} />;
}
