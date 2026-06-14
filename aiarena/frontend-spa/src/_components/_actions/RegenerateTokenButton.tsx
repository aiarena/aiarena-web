import { graphql, useFragment, useMutation } from "react-relay";

import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import SquareButton from "@/_components/_actions/SquareButton";
import { RegenerateTokenButtonMutation } from "./__generated__/RegenerateTokenButtonMutation.graphql";
import { RegenerateTokenButton_viewer$key } from "./__generated__/RegenerateTokenButton_viewer.graphql";

interface RegenerateTokenButtonProps {
  viewer: RegenerateTokenButton_viewer$key;
  outerClassName?: string;
}

export default function RegenerateTokenButton({
  viewer,
  outerClassName,
}: RegenerateTokenButtonProps) {
  const data = useFragment(
    graphql`
      fragment RegenerateTokenButton_viewer on Viewer {
        apiToken
      }
    `,
    viewer,
  );
  const hasToken = Boolean(data.apiToken);

  const [regenerateToken, regenerating] =
    useMutation<RegenerateTokenButtonMutation>(
      graphql`
        mutation RegenerateTokenButtonMutation {
          regenerateApiToken {
            viewer {
              ...TokenReveal_viewer
            }
            errors {
              messages
              field
            }
          }
        }
      `,
    );

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "regenerateApiToken",
    hasToken
      ? "API token regenerated successfully!"
      : "API token generated successfully!",
  );

  const handleRegenerate = () => {
    if (
      hasToken &&
      !window.confirm(
        "Regenerate your API token? Your current token will stop working immediately.",
      )
    ) {
      return;
    }
    regenerateToken({
      variables: {},
      onCompleted: (response, errors) => {
        onCompleted(response, errors);
      },
      onError,
    });
  };

  return (
    <SquareButton
      onClick={handleRegenerate}
      isLoading={regenerating}
      disabled={regenerating}
      text={hasToken ? "Regenerate" : "Generate"}
      outerClassName={outerClassName}
    />
  );
}
