import React, { useState } from "react";
import Modal from "../Modal";

import { Bot } from "@/_components/_display/ProfileBotOverviewList";
import TitleWrapper from "../TitleWrapper";
import Image from "next/image";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";

interface TrophiesModalProps {
  bot: Bot;
  isOpen: boolean;
  onClose: () => void;
}

interface SanitizedFile {
  name: string;
  size: number;
  type: string;
}

const BotZipUploadConfig = {
  allowedFileTypes: ["application/zip", "application/x-zip-compressed"],
  maxFileSize: 5 * 1024 * 1024, // 5MB
};

export default function SettingsModal({
  bot,
  isOpen,
  onClose,
}: TrophiesModalProps) {
  const [biography, setBiography] = useState(bot.biography || "");
  const [botZipUploadFile, setBotZipUploadFile] = useState<SanitizedFile | null>(
    null
  );
  const [uploadZipFileError, setUploadZipFileError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [botDataPubliclyDownloadable, setBotDataPubliclyDownloadable] =
    useState(bot.botDataPubliclyDownloadable || false);
  const [botDataEnabled, setBotDataEnabled] = useState(
    bot.botDataEnabled || false
  );

  const handleSaveBiography = () => {
    console.log("Biography saved:", biography);
    // Add logic to save the biography
  };

  const sanitizeFile = (file: File): SanitizedFile => {
    return {
      name: file.name,
      size: file.size,
      type: file.type,
    };
  };

  const validateFile = (file: File): boolean => {
    if (!BotZipUploadConfig.allowedFileTypes.includes(file.type)) {
      setUploadZipFileError("Invalid file type. Only ZIP files are allowed.");
      return false;
    }
    if (file.size > BotZipUploadConfig.maxFileSize) {
      setUploadZipFileError("File size exceeds the 5MB limit.");
      return false;
    }
    setUploadZipFileError("");
    return true;
  };

  const handleFileUpload = (file: File) => {
    if (validateFile(file)) {
      const sanitizedFile = sanitizeFile(file);
      setBotZipUploadFile(sanitizedFile);
      console.log("Sanitized file:", sanitizedFile);
    } else {
      setBotZipUploadFile(null);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleDrop = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setDragActive(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  return isOpen ? (
    <Modal onClose={onClose} title={`${bot.name} - Settings`}>
      <div className="space-y-4">
        <TitleWrapper title="Biography" />
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

        <TitleWrapper title="Settings" />
        <div className="flex flex-wrap space-x-2">
          <button
            className="bg-customGreen text-white py-2 px-4 space-x-2 rounded flex justify-center items-center"
            onClick={() => console.log("Download Bot Zip")}
          >
            <Image
              alt="Download Bot Zip Button"
              src={`${getPublicPrefix()}/icons/file-download.svg`}
              width={20}
              height={20}
              className="invert"
              style={{ width: 20, height: 20 }}
            />
            <p>Download Bot Zip</p>
          </button>

          {/* Drag and Drop Zone */}
          <label
            className={`border-2 ${
              dragActive ? "border-blue-500 bg-blue-50" : "border-gray-500"
            } border-dotted bg-gray-700 text-white py-2 px-4 space-x-2 rounded flex justify-center items-center cursor-pointer transition`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept={BotZipUploadConfig.allowedFileTypes.join(",")}
              className="hidden"
              onChange={handleInputChange}
            />
            <Image
              alt="Upload Bot Zip Button"
              src={`${getPublicPrefix()}/icons/file-upload.svg`}
              width={20}
              height={20}
              className="invert"
              style={{ width: 20, height: 20 }}
            />
            <p>Drag and Drop or Click to Upload</p>
          </label>
        </div>

        {/* Error Message */}
        {uploadZipFileError && (
          <p className="text-red-500 mt-2 text-sm ml">{uploadZipFileError}</p>
        )}
        {/* Uploaded File Info */}
        {botZipUploadFile && (
          <p className="text-customGreen mt-2 text-sm">
            Uploaded: {botZipUploadFile.name} ({botZipUploadFile.size} bytes)
          </p>
        )}

        <div className="flex items-center mt-2">
          <input
            type="checkbox"
            checked={botDataPubliclyDownloadable}
            onChange={() =>
              setBotDataPubliclyDownloadable(!botDataPubliclyDownloadable)
            }
            className="mr-2"
          />
          <label className="text-gray-300">
            Mark Bot Data Publicly Downloadable
          </label>
        </div>
        <div className="flex items-center mt-2">
          <input
            type="checkbox"
            checked={botDataEnabled}
            onChange={() => setBotDataEnabled(!botDataEnabled)}
            className="mr-2"
          />
          <label className="text-gray-300">Enable Bot Data</label>
        </div>
      </div>
    </Modal>
  ) : null;
}
