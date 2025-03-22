import React, { useState } from "react";
import Modal from "../Modal";

import { useUpdateUserBot } from "@/_components/_hooks/useUpdateUserBot";
import { graphql, useFragment } from "react-relay";
import { BotSettingsModal_bot$key } from "./__generated__/BotSettingsModal_bot.graphql";
import {
  useUpdateUserBotMutation,
  useUpdateUserBotMutation$data,
  useUpdateUserBotMutation$variables,
} from "@/_components/_hooks/__generated__/useUpdateUserBotMutation.graphql";

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

  const { updateBot, botInFlightField } = useUpdateUserBot();
  const botZip = bot.botZip;
  const [biography, setBiography] = useState(bot.wikiArticle || "");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const handleDownload = (url: string) => {
    const mirrorUrl = "https://aiarena.net/";
    console.log("Downloading: " + mirrorUrl + url);
    window.location.href = mirrorUrl + url;
  };

  const handleSaveBiography = () => {
    console.log("Biography saved:", biography);

    updateBot(bot.id, {
      wikiArticle: biography,
    });
    setHasUnsavedChanges(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setBiography(e.target.value);
    setHasUnsavedChanges(e.target.value !== bot.wikiArticle);
  };

  return isOpen ? (
    <Modal onClose={onClose} title={`${bot.name} - Settings`}>
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-gray-200">Biography</h3>
        <textarea
          className="w-full bg-gray-700 text-white p-2 rounded"
          rows={4}
          value={biography}
          onChange={handleChange}
        />
        {hasUnsavedChanges && (
          <p className="text-sm text-yellow-400">Unsaved changes</p>
        )}
        <button
          onClick={handleSaveBiography}
          className="w-full bg-customGreen text-white py-2 rounded"
        >
          Save Biography
        </button>

        <h3 className="text-lg font-bold text-gray-200">Bot Settings</h3>
        <button
          className="bg-customGreen text-white py-2 px-4 rounded w-full"
          onClick={() => handleDownload(botZip)}
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
              updateBot(bot.id, {
                botDataPubliclyDownloadable: !bot.botDataPubliclyDownloadable,
              })
            }
            disabled={botInFlightField === "botDataPubliclyDownloadable"}
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
              updateBot(bot.id, { botDataEnabled: !bot.botDataEnabled })
            }
            disabled={botInFlightField === "botDataEnabled"}
            className="mr-2"
          />
          <label className="text-gray-300">Enable Bot Data</label>
        </div>
      </div>
    </Modal>
  ) : null;
}
