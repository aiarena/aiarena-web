import MarkdownEditor from "@/_components/_props/MarkdownEditor";
import Modal from "@/_components/_props/Modal";
import { useState } from "react";

import { graphql, useFragment, useMutation } from "react-relay";
import { BotBiographyModal_bot$key } from "./__generated__/BotBiographyModal_bot.graphql";
import { BotBiographyModalMutation } from "./__generated__/BotBiographyModalMutation.graphql";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";

interface BotBiographyModalProps {
  bot: BotBiographyModal_bot$key;
  isOpen: boolean;
  onClose: () => void;
}

export default function BotBiographyModal({
  isOpen,
  onClose,
  ...props
}: BotBiographyModalProps) {
  const bot = useFragment(
    graphql`
      fragment BotBiographyModal_bot on BotType {
        wikiArticle
        id
        name
      }
    `,
    props.bot
  );
  const [updateBot, updating] = useMutation<BotBiographyModalMutation>(graphql`
    mutation BotBiographyModalMutation($input: UpdateBotInput!) {
      updateBot(input: $input) {
        bot {
          ...BotBiographyModal_bot
        }
        errors {
          field
          messages
        }
      }
    }
  `);

  const [biography, setBiography] = useState(bot.wikiArticle || "");

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "updateBot",
    "Bot Wiki Updated!"
  );

  const hasUnsavedWikiChanges =
    normalizeNewlines(biography) !== normalizeNewlines(bot.wikiArticle);
  function normalizeNewlines(s: string | null | undefined): string | undefined {
    if (s) {
      return s.replace(/\r\n/g, "\n");
    }
  }
  return isOpen ? (
    <>
      <Modal
        keepUnsetOnClose={true}
        isOpen={isOpen}
        onClose={onClose}
        title={`${bot.name} - Biography`}
        size="l"
      >
        <div className="h-[80vh] pb-4">
          <MarkdownEditor value={biography} setValue={setBiography} />
        </div>
        <button
          className={`w-full text-white py-2 rounded ${hasUnsavedWikiChanges ? "bg-customGreen" : "bg-slate-500"}`}
          disabled={updating}
          onClick={() => {
            updateBot({
              variables: {
                input: {
                  id: bot.id,
                  wikiArticle: biography,
                },
              },
              onCompleted: (...args) => {
                const success = onCompleted(...args);
                if (success) {
                  onClose();
                }
              },
              onError,
            });
          }}
        >
          Save
        </button>
      </Modal>
    </>
  ) : null;
}
