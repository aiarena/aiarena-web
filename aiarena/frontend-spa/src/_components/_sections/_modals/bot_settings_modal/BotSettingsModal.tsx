import { useState } from "react";

import { graphql, useFragment, useMutation } from "react-relay";
import { BotSettingsModal_bot$key } from "./__generated__/BotSettingsModal_bot.graphql";
import Modal from "@/_components/_props/Modal";
import { BotSettingsModalMutation } from "./__generated__/BotSettingsModalMutation.graphql";
import BiographyModal from "./BotBiographyModal";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import {
  ArrowUpOnSquareStackIcon,
  ArrowDownOnSquareStackIcon,
  FolderOpenIcon,
  ArrowUpOnSquareIcon,
  ArrowDownOnSquareIcon,
} from "@heroicons/react/20/solid";
import WideButton from "@/_components/_props/WideButton";
import { UploadFile } from "@/_components/_props/UploadFile";
import SectionDivider from "@/_components/_display/SectionDivider";
import SquareButton from "@/_components/_props/SquareButton";

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
  const [botDataFile, setBotDataFile] = useState<File | null>(null);

  const [isBiographyModalOpen, setBiographyModalOpen] = useState(false);
  // const fileInputRef = useRef<HTMLInputElement | null>(null);

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
          <WideButton
            onClick={() => setBiographyModalOpen(true)}
            title="Edit Bot Biography"
          />
          <div className="items-center mt-2">
            <div className="flex items-center mt-2">
              <label className="text-gray-300 flex items-center">
                Bot Data:
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
                  className="ml-2 w-5 h-5"
                  disabled={updating}
                />
              </label>
            </div>
            <div className=" mt-2">
              <label className="text-gray-300 flex items-center">
                Mark Bot Data Publicly Downloadable:
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
                  className="ml-2 w-5 h-5"
                />
              </label>
            </div>
          </div>
          <SectionDivider color="gray" />
          <div className="pt-4">
            <div className="pb-4 flex items-center justify-between gap-8 flex-wrap">
              <div className="min-w-[40%]">
                <h3 className="text-xl font-bold text-customGreen-light flex pb-2">
                  <FolderOpenIcon className="size-5 m-1" />
                  Bot Zip
                </h3>

                <button
                  className="mb-8 flex justify-center items-center w-full shadow-sm shadow-black border-2 text-white font-semibold py-1 px-2 rounded-sm transition duration-300 ease-in-out transform hover:shadow-customGreen border-customGreen bg-darken-2 hover:border-customGreen hover:bg-transparent"
                  onClick={() => handleDownload(bot.botZip)}
                  disabled={bot.botZip == "{}"}
                >
                  <ArrowDownOnSquareStackIcon
                    className="size-6 mr-2"
                    title="Download ZIP"
                  />
                  Download Bot Zip
                </button>

                <UploadFile
                  accept=".zip"
                  file={botZipFile}
                  setFile={setBotZipFile}
                  id={"bot-zip-file-upload"}
                />

                <button
                  className={`mt-4 flex justify-center items-center w-full shadow-sm shadow-black border-2 text-white font-semibold py-1 px-2 rounded-sm transition duration-300 ease-in-out transform ${
                    botZipFile
                      ? "hover:shadow-customGreen border-customGreen bg-darken-2 hover:border-customGreen hover:bg-transparent"
                      : "bg-darken border-gray-700 hover:bg-darken hover:border-gray-700 "
                  }`}
                  onClick={() => {
                    if (!botZipFile) return;
                    updateBot({
                      variables: {
                        input: { id: bot.id, botZip: null },
                      },
                      uploadables: {
                        "input.botZip": botZipFile,
                      },
                      onCompleted: (...args) => {
                        const success = onCompleted(...args);
                        if (success) setBotZipFile(null);
                        onCompleted(...args);
                      },
                      onError,
                    });
                  }}
                >
                  <ArrowUpOnSquareStackIcon className="size-5" />
                  Upload Bot Zip
                </button>
              </div>

              {/* Bot Data */}
              <div className="min-w-[40%]">
                <div className="flex items-center gap-2  pb-4">
                  <h3 className="text-xl font-bold text-customGreen-light flex">
                    <FolderOpenIcon className="size-5 m-1" />
                  Bot Data
                </h3>
                  <a
                    href="/wiki/bot-development/#wiki-toc-bot-memory-the-data-folder"
                    target="_blank"
                    className="pt-1"
                  >
                    Wiki
                  </a>
                </div>

                <SquareButton
                  disabled={!bot.botData}
                  onClick={() =>
                    bot.botData ? handleDownload(bot.botData) : null
                  }
                  outerClassName="w-full mb-8"
                >
                  <ArrowDownOnSquareStackIcon
                    className="size-6 mr-1"
                    title="Download Data"
                  />
                  Download Bot Data
                </SquareButton>

                <UploadFile
                  accept=".zip"
                  file={botDataFile}
                  setFile={setBotDataFile}
                  id={"bot-data-file-upload"}
                />
                <SquareButton
                  disabled={!botDataFile}
                  onClick={() => {
                    if (!botDataFile) return;
                    updateBot({
                      variables: {
                        input: { id: bot.id, botData: null },
                      },
                      uploadables: {
                        "input.botData": botDataFile,
                      },
                      onCompleted: (...args) => {
                        const success = onCompleted(...args);
                        if (success) setBotDataFile(null);
                        onCompleted(...args);
                      },
                      onError,
                    });
                  }}
                  outerClassName="w-full mt-4"
                >
                  <ArrowUpOnSquareStackIcon className="size-5 mr-1" />
                  Upload Bot Data
                </SquareButton>
              </div>
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
