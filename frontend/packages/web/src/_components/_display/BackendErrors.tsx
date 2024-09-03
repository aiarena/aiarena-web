import PropTypes from "prop-types";
import React from "react";
import Alert from "@/_components/_display/Alert";

function getMessageList({ formErrors, graphqlErrors, failError }) {
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

  return [...formMessages, ...graphqlMessages, ...failMessages];
}

export default function BackendErrors({
  formErrors = [],
  graphqlErrors = [],
  failError = null,
  ...props
}) {
  const finalMessages = getMessageList({
    formErrors,
    graphqlErrors,
    failError,
  });

  if (!finalMessages.length) {
    return null;
  }

  const message = finalMessages.join(', ');

  return <Alert message={message} />;
}

BackendErrors.propTypes = {
  formErrors: PropTypes.array,
  graphqlErrors: PropTypes.array,
  failError: PropTypes.object,
};
