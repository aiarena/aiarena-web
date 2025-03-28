import { graphql, useMutation } from "react-relay";
import { useUpdateUserBotMutation } from "./__generated__/useUpdateUserBotMutation.graphql";
import { useState } from "react";

const mutation = graphql`
  mutation useUpdateUserBotMutation($input: UpdateBotInput!) {
    updateBot(input: $input) {
      bot {
        id
        botDataEnabled
        botDataPubliclyDownloadable
        botZipPubliclyDownloadable
        wikiArticle
      }
    }
  }
`;

export const useUpdateUserBot = () => {
  const [commit] = useMutation<useUpdateUserBotMutation>(mutation);
  const [botInFlightField, setBotInFlightField] = useState<string | null>(null); // Track specific field

  const updateBot = (
    botId: string,
    updatedFields: Partial<{
      botDataEnabled: boolean;
      botDataPubliclyDownloadable: boolean;
      botZipPubliclyDownloadable: boolean;
      wikiArticle: string;
    }>,
  ) => {
    return new Promise((resolve, reject) => {
      const fieldBeingUpdated = Object.keys(updatedFields)[0]; // Track only the first field
      setBotInFlightField(fieldBeingUpdated); // Set the specific field in flight
      commit({
        variables: {
          input: {
            id: botId,
            ...updatedFields,
          },
        },
        onCompleted: (data) => {
          setBotInFlightField(null);
          resolve(data);
        },
        onError: (err) => {
          console.error("Mutation error:", err);
          setBotInFlightField(null);
          reject(err);
        },
      });
    });
  };

  return { updateBot, botInFlightField };
};
