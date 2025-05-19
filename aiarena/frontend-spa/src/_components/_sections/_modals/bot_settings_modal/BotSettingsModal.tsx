import { useRef, useState } from "react";

import { graphql, useFragment, useMutation } from "react-relay";
import { BotSettingsModal_bot$key } from "./__generated__/BotSettingsModal_bot.graphql";
import Modal from "@/_components/_props/Modal";
import { BotSettingsModalMutation } from "./__generated__/BotSettingsModalMutation.graphql";
import BiographyModal from "./BotBiographyModal";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";

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
        ...BotBiographyModal_bot
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
          botZip
        }
        errors {
          field
          messages
        }
      }
    }
  `);

  const [botZipFile, setBotZipFile] = useState<File | null>(null);
  const [isBiographyModalOpen, setBiographyModalOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleDownload = (url: string) => {
    window.location.href = `/${url}`;
  };

  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "updateBot",
    "Bot Settings Updated!"
  );

  return (
    <>
      <Modal onClose={onClose} isOpen={isOpen} title={`Settings - ${bot.name}`}>
        <div className="space-y-4">
          <button
            className="bg-customGreen text-white py-2 px-4 rounded w-full"
            onClick={() => setBiographyModalOpen(true)}
          >
            Edit Bot Biography
          </button>

          <h3 className="text-lg font-bold text-gray-200">Bot Settings</h3>
          <button
            className="bg-customGreen text-white py-2 px-4 rounded w-full"
            onClick={() => handleDownload(bot.botZip)}
            disabled={bot.botZip == "{}"}
          >
            Download Bot Zip
          </button>
          <label className="block">
            <span className="text-gray-300">Bot ZIP:</span>
            <input
              type="file"
              ref={fileInputRef}
              className="w-full bg-gray-700 text-white p-2 rounded"
              onChange={(e) => {
                if (e.target.files != null) {
                  setBotZipFile(e.target.files[0]);
                } else {
                  setBotZipFile(null);
                }
              }}
            />
          </label>
          <button
            className={`w-full text-white py-2 rounded ${botZipFile ? "bg-customGreen" : "bg-slate-500"}`}
            onClick={() => {
              if (!botZipFile) return;
              updateBot({
                variables: {
                  input: {
                    id: bot.id,
                    botZip: null,
                  },
                },
                uploadables: {
                  "input.botZip": botZipFile,
                },
                onCompleted: (...args) => {
                  const success = onCompleted(...args);
                  if (success) {
                    setBotZipFile(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = "";
                    }
                  }
                  onCompleted(...args);
                },
                onError,
              });
            }}
          >
            Upload Bot Zip
          </button>
          <div className="items-center mt-2">
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
                    onCompleted: (...args) => {
                      onCompleted(...args);
                    },
                    onError,
                  })
                }
                disabled={updating}
                className="mr-2"
              />
              <label className="text-gray-300">Enable Bot Data</label>
            </div>
          </div>
        </div>
      </Modal>

      {isBiographyModalOpen && (
        <BiographyModal
          isOpen={isBiographyModalOpen}
          onClose={() => setBiographyModalOpen(false)}
          bot={bot}
        />
      )}
    </>
  );
}
