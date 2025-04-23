import React, { useState } from "react";
import Modal from "../_props/Modal";

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

export default function UploadBotModal({ isOpen, onClose }: UploadBotModal) {
  const [name, setName] = useState("");
  const [race, setRace] = useState("Zerg");
  const [type, setType] = useState("AI");
  const [botDataEnabled, setBotDataEnabled] = useState(false);

  const handleUpload = () => {
    console.log("Uploading Bot", { name, race, type, botDataEnabled });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <Modal onClose={onClose} title="Upload Bot">
      <div className="space-y-4">
        <label className="block">
          <span className="text-gray-300">Name:</span>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-gray-700 text-white p-2 rounded"
          />
        </label>

        <label className="block">
          <span className="text-gray-300">Bot ZIP:</span>
          <input
            type="file"
            className="w-full bg-gray-700 text-white p-2 rounded"
          />
          <p className="text-sm text-gray-500">Ingen fil har valts</p>
        </label>

        <label className="block">
          <span className="text-gray-300">Bot Data Enabled:</span>
          <input
            type="checkbox"
            checked={botDataEnabled}
            onChange={(e) => setBotDataEnabled(e.target.checked)}
            className="ml-2"
          />
        </label>

        <label className="block">
          <span className="text-gray-300">Plays Race:</span>
          <select
            value={race}
            onChange={(e) => setRace(e.target.value)}
            className="w-full bg-gray-700 text-white p-2 rounded"
          >
            <option value="Zerg">Zerg</option>
            <option value="Terran">Terran</option>
            <option value="Protoss">Protoss</option>
          </select>
        </label>

        <label className="block">
          <span className="text-gray-300">Type:</span>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="w-full bg-gray-700 text-white p-2 rounded"
          >
            <option value="AI">AI</option>
            <option value="Script">Script</option>
          </select>
        </label>

        <button
          onClick={handleUpload}
          className="w-full bg-customGreen text-white py-2 rounded"
        >
          Upload
        </button>
      </div>
    </Modal>
  );
}
