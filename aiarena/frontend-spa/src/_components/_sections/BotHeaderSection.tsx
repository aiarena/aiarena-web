import { useState } from "react";

import { getPublicPrefix } from "@/_lib/getPublicPrefix";

import { graphql, useFragment } from "react-relay";
import { formatDate } from "@/_lib/dateUtils";
import BotSettingsModal from "./_modals/bot_settings_modal/BotSettingsModal";
import { BotHeaderSection_bot$key } from "./__generated__/BotHeaderSection_bot.graphql";
import UnderlineButton from "../_props/UnderlineButton";
import { extractRelayID, getNodes } from "@/_lib/relayHelpers";
import BotAllParticipationsModal from "./_modals/BotAllParticipationsModal";
import BotTrophiesModal from "./_modals/BotTrophiesModal";

export interface BotHeaderSectionProps {
  bot: BotHeaderSection_bot$key;
}

export default function BotHeaderSection(props: BotHeaderSectionProps) {
  const bot = useFragment(
    graphql`
      fragment BotHeaderSection_bot on BotType {
        id
        name
        created
        type
        botZipUpdated
        trophies {
          edges {
            node {
              name
              trophyIconImage
              trophyIconName
            }
          }
        }
        ...BotSettingsModal_bot
        ...BotAllParticipationsModal_bot
        ...BotTrophiesModal_bot
      }
    `,
    props.bot
  );

  const [isTrophiesModalOpen, setTrophiesModalOpen] = useState(false);
  const [isSettingsModalOpen, setSettingsModalOpen] = useState(false);
  const [isAllParticipationsModalOpen, setAllParticipationsModalOpen] =
    useState(false);
  return (
    <div className="p-4 border-b border-gray-600 bg-gray-900 rounded-t-lg">
      {/* Grid Layout: Mobile: 1 col, Desktop: 3 cols */}
      <div className="text-left space-y-2">
        <div className="flex justify-between flsex-wrap">
          <div className="flex items-center flex-wrap">
            {/* Bot Name */}
            <a
              href={`/bots/${extractRelayID(bot.id, "BotType")}`}
              className="font-bold text-lg text-customGreen font-gugi font-light"
            >
              {bot.name}
            </a>

            {/*/!* Trophy Icon and Count *!/*/}

            <div
              className="flex items-center cursor-pointer hover:bg-slate-700 rounded p-1 ml-2"
              onClick={() => setTrophiesModalOpen(true)}
            >
              <img
                src={`${getPublicPrefix()}/icons/trophy.svg`}
                alt="Trophy Icon"
                width={20}
                height={20}
              />
              <span className="ml-1 text-lg font-bold text-gray-300">
                {getNodes(bot?.trophies).length || 0}
              </span>
            </div>
          </div>

          {/* Settings Button */}

          <div
            className="cursor-pointer hover:bg-slate-700 py-1 px-2 ml-2 flex justify-center rounded-md border-slate-700 border"
            onClick={() => setSettingsModalOpen(true)}
          >
            <img
              alt="Open Settings"
              src={`${getPublicPrefix()}/icons/cogwheel.svg`}
              width={20}
              height={20}
              className="invert"
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
            <UnderlineButton
              onClick={() => {
                setAllParticipationsModalOpen(true);
              }}
            >
              View all participations
            </UnderlineButton>
          </div>
        </div>
      </div>

      {/* Modals */}

      {isSettingsModalOpen && (
        <BotSettingsModal
          bot={bot}
          isOpen={isSettingsModalOpen}
          onClose={() => setSettingsModalOpen(false)}
        />
      )}

      {isAllParticipationsModalOpen && (
        <BotAllParticipationsModal
          bot={bot}
          isOpen={isAllParticipationsModalOpen}
          onClose={() => setAllParticipationsModalOpen(false)}
        />
      )}
      {isTrophiesModalOpen && (
        <BotTrophiesModal
          bot={bot}
          isOpen={isTrophiesModalOpen}
          onClose={() => setTrophiesModalOpen(false)}
        />
      )}
    </div>
  );
}
