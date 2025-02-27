import React, { useState } from "react";
import Modal from "../Modal";

import { Bot } from "@/_components/_display/ProfileBotOverviewList";
import { useUpdateUserBot } from "@/_components/_hooks/useUpdateUserBot";

interface TrophiesModalProps {
  bot: Bot;
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({
  bot,
  isOpen,
  onClose,
}: TrophiesModalProps) {
  const { updateBot, botInFlightField } = useUpdateUserBot();
  const [botZip] = useState(bot.botZip || "");
  const [biography, setBiography] = useState(bot.wikiArticle);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const handleDownload = (url: string) => {
    const mirrorUrl = "https://aiarena.net/";
    console.log("Downloading: " + mirrorUrl + url);
    window.location.href = mirrorUrl + url;
  };

  const handleSaveBiography = () => {
    console.log("Biography saved:", biography);
    // Simulate API save call here
    updateBot(bot.id, {
      wikiArticleContent: biography,
    })
    setHasUnsavedChanges(false); // Reset unsaved changes tracking
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
