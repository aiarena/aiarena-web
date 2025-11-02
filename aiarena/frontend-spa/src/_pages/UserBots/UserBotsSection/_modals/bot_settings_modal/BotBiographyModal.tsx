import MarkdownEditor from "@/_components/_actions/MarkdownEditor";
import Modal from "@/_components/_actions/Modal";
import { useState } from "react";

import { graphql, useFragment, useMutation } from "react-relay";
import { BotBiographyModal_bot$key } from "./__generated__/BotBiographyModal_bot.graphql";
import { BotBiographyModalMutation } from "./__generated__/BotBiographyModalMutation.graphql";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import WideButton from "@/_components/_actions/WideButton";
import useUnsavedSince from "@/_components/_hooks/useUnsavedSince";

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

  const { seconds, resetBaseline } = useUnsavedSince(hasUnsavedWikiChanges);

  const statusText = hasUnsavedWikiChanges
    ? `You have unsaved changes. Last saved ${seconds} seconds ago.`
    : "You have no unsaved changes.";

  return (
    <>
      <Modal
        keepUnsetOnClose={true}
        onClose={onClose}
        isOpen={isOpen}
        title={`${bot.name} - Biography`}
        size="l"
      >
        <div className="h-[80vh] pb-20">
          <MarkdownEditor value={biography} setValue={setBiography} />
          <p className="py-4 pl-2 text-gray-300">{statusText}</p>

          <WideButton
            title="Save"
            loading={updating}
            type="button"
            disabled={!hasUnsavedWikiChanges}
            onClick={() => {
              updateBot({
                variables: {
                  input: {
                    id: bot.id,
                    wikiArticle: biography,
                  },
                },
                onCompleted: (...args) => {
                  onCompleted(...args);
                  resetBaseline();
                },
                onError,
              });
            }}
          />
        </div>
      </Modal>
    </>
  );
}
