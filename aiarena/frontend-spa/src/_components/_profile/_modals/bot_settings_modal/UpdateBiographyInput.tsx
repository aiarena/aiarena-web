import { graphql, useFragment, useMutation } from "react-relay";
import { UpdateBiographyInputMutation } from "./__generated__/UpdateBiographyInputMutation.graphql";
import { UpdateBiographyInput_bot$key } from "./__generated__/UpdateBiographyInput_bot.graphql";
import { useState } from "react";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers.tsx";

interface UpdateBiographyInputProps {
  bot: UpdateBiographyInput_bot$key;
}

export default function UpdateBiographyInput(props: UpdateBiographyInputProps) {
  const bot = useFragment(
    graphql`
      fragment UpdateBiographyInput_bot on BotType {
        id
        wikiArticle
      }
    `,
    props.bot,
  );

  const [updateBot, updating] = useMutation<UpdateBiographyInputMutation>(
    graphql`
      mutation UpdateBiographyInputMutation($input: UpdateBotInput!) {
        updateBot(input: $input) {
          bot {
            ...UpdateBiographyInput_bot
          }
          errors {
            field
            messages
          }
        }
      }
    `,
  );

  const [biography, setBiography] = useState(bot.wikiArticle || "");
  const hasUnsavedWikiChanges = biography !== bot.wikiArticle;

  const handlers = useSnackbarErrorHandlers("updateBot", "Bot Wiki Updated!");

  return (
    <>
      <h3 className="text-lg font-bold text-gray-200">Biography</h3>
      <textarea
        className="w-full bg-gray-700 text-white p-2 rounded"
        rows={4}
        value={biography}
        onChange={(e) => {
          setBiography(e.target.value);
        }}
      />
      <button
        disabled={updating}
        onClick={() => {
          updateBot({
            variables: {
              input: {
                id: bot.id,
                wikiArticle: biography,
              },
            },
            ...handlers,
          });
        }}
        className={`w-full text-white py-2 rounded ${hasUnsavedWikiChanges ? "bg-customGreen" : "bg-slate-500"}`}
      >
        Save Biography
      </button>
    </>
  );
}
