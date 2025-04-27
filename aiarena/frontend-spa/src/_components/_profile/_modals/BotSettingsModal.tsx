import React, { useState } from "react";

import { graphql, useFragment, useMutation } from "react-relay";
import { BotSettingsModal_bot$key } from "./__generated__/BotSettingsModal_bot.graphql";
import Modal from "@/_components/_props/Modal";
import { BotSettingsModalMutation } from "./__generated__/BotSettingsModalMutation.graphql";

interface BotSettingsModalProps {
  bot: BotSettingsModal_bot$key;
  isOpen: boolean;
  onClose: () => void;
}

export default function BotSettingsModal({
  isOpen,
  onClose,
  ...props
}: BotSettingsModalProps) {
  const bot = useFragment(
    graphql`
      fragment BotSettingsModal_bot on BotType {
        id
        name
        url
        botData
        botDataEnabled
        botDataPubliclyDownloadable
        botZip
        botZipPubliclyDownloadable
        botZipUpdated
        wikiArticle
      }
    `,
    props.bot
  );

  const [updateBot, updating] = useMutation<BotSettingsModalMutation>(graphql`
    mutation BotSettingsModalMutation($input: UpdateBotInput!) {
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
  `);

  // const { updateBot, botInFlightField } = useUpdateUserBot();
  const [biography, setBiography] = useState(bot.wikiArticle || "");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const handleDownload = (url: string) => {
    window.location.href = `/${url}`;
  };

  return isOpen ? (
    <Modal onClose={onClose} title={`${bot.name} - Settings`}>
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-gray-200">Biography</h3>
        <textarea
          className="w-full bg-gray-700 text-white p-2 rounded"
          rows={4}
          value={biography}
          onChange={(e) => {
            setBiography(e.target.value);
            setHasUnsavedChanges(e.target.value !== bot.wikiArticle);
          }}
        />
        {hasUnsavedChanges && (
          <p className="text-sm text-yellow-400">Unsaved changes</p>
        )}

        <button
          onClick={() => {
            updateBot({
              variables: {
                input: {
                  id: bot.id,
                  wikiArticle: biography,
                },
              },
            });
            setHasUnsavedChanges(false);
          }}
          className="w-full bg-customGreen text-white py-2 rounded"
        >
          Save Biography
        </button>

        <h3 className="text-lg font-bold text-gray-200">Bot Settings</h3>
        <button
          className="bg-customGreen text-white py-2 px-4 rounded w-full"
          onClick={() => handleDownload(bot.botZip)}
        >
          Download Bot Zip
        </button>
        <button
          className="bg-gray-700 text-white py-2 px-4 rounded w-full mt-2"
          onClick={() => console.log("Upload Bot Zip")}
        >
          Upload Bot Zip
        </button>

        <div className="flex items-center mt-2">
          <input
            type="checkbox"
            checked={bot.botDataPubliclyDownloadable}
            onChange={() =>
              updateBot({
                variables: {
                  input: {
                    id: bot.id,
                    botDataPubliclyDownloadable:
                      !bot.botDataPubliclyDownloadable,
                  },
                },
              })
            }
            disabled={updating}
            className="mr-2"
          />
          <label className="text-gray-300">
            Mark Bot Data Publicly Downloadable
          </label>
        </div>
        <div className="flex items-center mt-2">
          <input
            type="checkbox"
            checked={bot.botDataEnabled}
            onChange={() =>
              updateBot({
                variables: {
                  input: {
                    id: bot.id,
                    botDataEnabled: !bot.botDataEnabled,
                  },
                },
              })
            }
            disabled={updating}
            className="mr-2"
          />
          <label className="text-gray-300">Enable Bot Data</label>
        </div>
      </div>
    </Modal>
  ) : null;
}
