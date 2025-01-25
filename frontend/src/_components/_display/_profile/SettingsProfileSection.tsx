import { useState } from "react";
import Image from "next/image";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import { User } from "@/_components/_hooks/useUser";

interface SettingsProfileSection {
  user: User;
}

export default function SettingsProfileSection({
  user,
}: SettingsProfileSection) {
  const [apiTokenVisible, setApiTokenVisible] = useState(false);
  const [apiToken, setApiToken] = useState(
    "sk_test_********************************"
  );
  const [discordLinked, setDiscordLinked] = useState(false);
  const [patreonLinked, setPatreonLinked] = useState(false);

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");

  const handleLinkDiscord = () => setDiscordLinked(true);
  const handleUnlinkDiscord = () => setDiscordLinked(false);
  const handleLinkPatreon = () => setPatreonLinked(true);
  const handleUnlinkPatreon = () => setPatreonLinked(false);

  const handleCopyToken = () => {
    navigator.clipboard.writeText(apiToken);
    alert("API token copied!");
  };

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword === confirmNewPassword) {
      alert("Password changed!");
      setOldPassword("");
      setNewPassword("");
      setConfirmNewPassword("");
    } else {
      alert("Passwords do not match!");
    }
  };

  return (
    <div className="space-y-6 text-sm max-w-lg w-full">
      {/* Profile Overview */}
      <div className="bg-gray-700 p-4 rounded-md space-y-2">
        <h3 className="text-base font-semibold text-customGreen">Profile</h3>
        <div className="flex space-x-3 space-y-2 justify-between flex-wrap">
          <div className="flex">
          <div className="relative w-12 h-12 flex-shrink-0">
            <Image
              src={`${getPublicPrefix()}/assets_logo/img/default_avatar.jpg`}
              alt="User avatar"
              fill
              className="object-cover"
            />
            <>
              {user.patreonLevel && user.patreonLevel != "Bronze" ? (
                <div className="absolute inset-0 border-2 border-customGreen"></div>
              ) : null}
            </>
          </div>
          <div className="leading-tight p-2">
            <p className="text-white font-bold">{user.username}</p>
            {user.patreonLevel && user.patreonLevel == "NONE" ? (
              <p className="text-customGreen text-xs">Supporter</p>
            ) : null}
          </div>
          </div>
          <div className="flex items-center space-x-2">
            <svg
              className="w-4 h-4 text-indigo-400"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M20.317 4.369A19.791 19.791 0 0016.845 3c-.247.454-.53 1.047-.721 1.514a17.835 17.835 0 00-4.248 0c-.191-.467-.474-1.06-.721-1.514A19.781 19.781 0 003.683 4.37C.976 9.05 0 13.5 0 17.752c0 0 4.144 3.697 8.298 3.697h.878a7.548 7.548 0 007.547-7.547c0-.056 0-.11-.002-.165 1.102-.794 2.03-1.695 2.805-2.7a19.248 19.248 0 001.79-2.6z" />
            </svg>
            <span className="text-gray-300">Discord:</span>
            {discordLinked ? (
              <button
                onClick={handleUnlinkDiscord}
                className="text-white bg-red-500 px-2 py-0.5 rounded hover:bg-red-400"
              >
                Unlink
              </button>
            ) : (
              <button
                onClick={handleLinkDiscord}
                className="text-white bg-indigo-500 px-2 py-0.5 rounded hover:bg-indigo-400"
              >
                Link
              </button>
            )}
          </div>

          {/* Patreon */}
          <div className="flex items-center space-x-2">
            <svg
              className="w-4 h-4 text-red-400"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <circle cx="12" cy="12" r="9" />
            </svg>
            <span className="text-gray-300">Patreon:</span>
            {patreonLinked ? (
              <button
                onClick={handleUnlinkPatreon}
                className="text-white bg-red-500 px-2 py-0.5 rounded hover:bg-red-400"
              >
                Unlink
              </button>
            ) : (
              <button
                onClick={handleLinkPatreon}
                className="text-white bg-indigo-500 px-2 py-0.5 rounded hover:bg-indigo-400"
              >
                Link
              </button>
            )}
          </div>
        </div>
      </div>

      {/* API Token */}
      <div className="bg-gray-700 p-4 rounded-md space-y-2">
        <h3 className="text-base font-semibold text-customGreen">API Token</h3>
        <div className="flex flex-wrap items-center gap-2">
          <span className="bg-gray-800 text-gray-300 px-2 py-1 rounded font-mono text-xs max-w-full truncate">
            {apiTokenVisible ? apiToken : "•••••••••••••••••••••••"}
          </span>
          <button
            onClick={() => setApiTokenVisible(!apiTokenVisible)}
            className="text-white bg-indigo-500 px-2 py-0.5 rounded hover:bg-indigo-400"
          >
            {apiTokenVisible ? "Hide" : "Show"}
          </button>
          <button
            onClick={handleCopyToken}
            className="text-white bg-gray-600 px-2 py-0.5 rounded hover:bg-gray-500"
          >
            Copy
          </button>
        </div>
      </div>

      {/* Change Password */}
      <div className="bg-gray-700 p-4 rounded-md">
        <h3 className="text-base font-semibold text-customGreen mb-2">
          Change Password
        </h3>
        <form onSubmit={handleChangePassword} className="space-y-3">
          <div className="flex flex-col max-w-xs w-full">
            <label className="block text-gray-300 text-xs mb-1">
              Old Password
            </label>
            <input
              type="password"
              className="w-full p-1 bg-gray-800 text-white rounded border border-gray-600 text-xs 
                         focus:outline-none focus:ring-1 focus:ring-customGreen focus:border-customGreen"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
            />
          </div>
          <div className="flex flex-col max-w-xs w-full">
            <label className="block text-gray-300 text-xs mb-1">
              New Password
            </label>
            <input
              type="password"
              className="w-full p-1 bg-gray-800 text-white rounded border border-gray-600 text-xs 
                         focus:outline-none focus:ring-1 focus:ring-customGreen focus:border-customGreen"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>
          <div className="flex flex-col max-w-xs w-full">
            <label className="block text-gray-300 text-xs mb-1">
              Confirm New Password
            </label>
            <input
              type="password"
              className="w-full p-1 bg-gray-800 text-white rounded border border-gray-600 text-xs 
                         focus:outline-none focus:ring-1 focus:ring-customGreen focus:border-customGreen"
              value={confirmNewPassword}
              onChange={(e) => setConfirmNewPassword(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="text-white bg-customGreen px-3 py-1 rounded text-xs hover:bg-green-500"
          >
            Update
          </button>
        </form>
      </div>
    </div>
  );
}
