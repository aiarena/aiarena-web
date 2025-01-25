import React, { useState } from "react";
import Image from "next/image";
import { getPublicPrefix } from "@/_lib/getPublicPrefix";
import TrophiesModal from "@/_components/_display/_profile/BotTrophiesModal";
import SettingsModal from "@/_components/_display/_profile/BotSettingsModal";
import { formatDate } from "@/_lib/dateUtils";
import { ProfileBotProps } from "@/_components/_display/ProfileBot";

export default function BotHeaderSection({ bot }: ProfileBotProps) {
  const [isTrophiesModalOpen, setTrophiesModalOpen] = useState(false);
  const [isSettingsModalOpen, setSettingsModalOpen] = useState(false);
  
  return (
    <div className="p-4 border-b border-gray-600 bg-gray-900 rounded-t-lg">
      {/* Grid Layout: Mobile: 1 col, Desktop: 3 cols */}
      <div className="text-left space-y-2">
        <div className="flex justify-between flex-wrap">
          <div className="flex items-center flex-wrap">
            {/* Bot Name */}
            <h3 className="font-bold text-lg text-customGreen">{bot.name}</h3>

            {/* Trophy Icon and Count */}
            <div
              className="flex items-center cursor-pointer hover:bg-slate-700 rounded p-1 ml-2"
              onClick={() => setTrophiesModalOpen(true)}
            >
              <Image
                src={`${getPublicPrefix()}/icons/trophy.svg`}
                alt="Trophy Icon"
               
                width={20}
                height={20}

              />
              <span className="ml-1 text-lg font-bold text-gray-300">
                {bot?.trophies?.length || 0}
              </span>
            </div>
          </div>

          {/* Settings Button */}

          <div
            className="cursor-pointer hover:bg-slate-700 py-1 px-2 ml-2 flex justify-center rounded-md border-slate-700 border items-center"
            onClick={() => setSettingsModalOpen(true)}
          >
            <Image
              alt="Open Settings"
              src={`${getPublicPrefix()}/icons/cogwheel.svg`}
                
                width={20}
                height={20}
              className="invert"
              style={{ width: 20, height: 20 }}
            />
          </div>
        </div>

        <div className="justify-between flex">
          {/* Left List */}
          {/* Bot Details */}
          <div>
            <p className="text-sm text-gray-400">
              <span className="font-bold">Game:</span> Starcraft II
            </p>
            {bot.race && (
              <p className="text-sm text-gray-400">
                <span className="font-bold">Race:</span> {bot.race}
              </p>
            )}
              {bot.type && (
              <p className="text-sm text-gray-400">
                <span className="font-bold">Type:</span> {bot.type}
              </p>
            )}
            {bot.botZipUpdated && (
              <p className="text-sm text-gray-400">
                <span className="font-bold">Zip Updated:</span>{" "}
                {formatDate(bot.botZipUpdated)}
              </p>
            )}
          </div>
          {/* Right list */}
          <div>
            {" "}
            <button className="mt-2 text-customGreen underline">
              Activity log
            </button>
          </div>
        </div>
      </div>

      {/* Modals */}
      {isTrophiesModalOpen && (
        <TrophiesModal
          bot={bot}
          isOpen={isTrophiesModalOpen}
          onClose={() => setTrophiesModalOpen(false)}
        />
      )}
      {isSettingsModalOpen && (
        <SettingsModal
          bot={bot}
          isOpen={isSettingsModalOpen}
          onClose={() => setSettingsModalOpen(false)}
        />
      )}
    </div>
  );
}
