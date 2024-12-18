import React, { useState } from "react";
import Modal from "../Modal";

import { Bot } from "@/_components/_display/ProfileBotOverviewList";

interface TrophiesModalProps {
  bot: Bot;
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ bot, isOpen, onClose }: TrophiesModalProps) {
  const [biography, setBiography] = useState(bot.biography || "");
  const [isZipPublic, setIsZipPublic] = useState(bot.isZipPublic || false);
  const [isDataPublic, setIsDataPublic] = useState(bot.isDataPublic || false);
  const [isDataEnabled, setIsDataEnabled] = useState(bot.isDataEnabled || false);

  const handleSaveBiography = () => {
    console.log("Biography saved:", biography);
    // Add logic to save the biography
  };

  return isOpen ? (
    <Modal onClose={onClose} title={`${bot.name} - Settings`}>
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-gray-200">Biography</h3>
        <textarea
          className="w-full bg-gray-700 text-white p-2 rounded"
          rows={4}
          value={biography}
          onChange={(e) => setBiography(e.target.value)}
        />
        <button
          onClick={handleSaveBiography}
          className="w-full bg-customGreen text-white py-2 rounded"
        >
          Save Biography
        </button>

        <h3 className="text-lg font-bold text-gray-200">Bot Settings</h3>
        <button
          className="bg-customGreen text-white py-2 px-4 rounded w-full"
          onClick={() => console.log("Download Bot Zip")}
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
            checked={isZipPublic}
            onChange={() => setIsZipPublic(!isZipPublic)}
            className="mr-2"
          />
          <label className="text-gray-300">Mark Bot Zip Publicly Downloadable</label>
        </div>
        <div className="flex items-center mt-2">
          <input
            type="checkbox"
            checked={isDataPublic}
            onChange={() => setIsDataPublic(!isDataPublic)}
            className="mr-2"
          />
          <label className="text-gray-300">Mark Bot Data Publicly Downloadable</label>
        </div>
        <div className="flex items-center mt-2">
          <input
            type="checkbox"
            checked={isDataEnabled}
            onChange={() => setIsDataEnabled(!isDataEnabled)}
            className="mr-2"
          />
          <label className="text-gray-300">Enable Bot Data</label>
        </div>
      </div>
    </Modal>
  ) : null;
}
