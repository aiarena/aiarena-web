import { useState } from "react";
import { graphql, useFragment } from "react-relay";
import { formatDate } from "@/_lib/dateUtils";
import BotSettingsModal from "./_modals/bot_settings_modal/BotSettingsModal";
import { BotHeaderSection_bot$key } from "./__generated__/BotHeaderSection_bot.graphql";
import UnderlineButton from "../_props/UnderlineButton";
import { extractRelayID, getNodes } from "@/_lib/relayHelpers";
import BotAllParticipationsModal from "./_modals/BotAllParticipationsModal";
import BotTrophiesModal from "./_modals/BotTrophiesModal";
import { TrophyIcon, CogIcon } from "@heroicons/react/20/solid";

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
    <div className="p-4 border-b border-gray-800 bg-[linear-gradient(240deg,rgb(0,0,0,0.3)_0%,rgba(0,0,0,0.9)_100%)]  rounded-t-lg">
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

            <div
              className="flex items-center cursor-pointer hover:bg-neutral-700 rounded p-1 ml-2"
              onClick={() => setTrophiesModalOpen(true)}
              title="Bot Trophies"
            >
              <TrophyIcon
                aria-label="Trophy icon"
                className=" size-5 text-white"
                role="img"
              />

              <span className="ml-1 text-lg font-bold text-gray-300">
                {getNodes(bot?.trophies).length || 0}
              </span>
            </div>
          </div>

          {/* Settings Button */}

          <div
            className="cursor-pointer hover:bg-neutral-700 py-1 px-2 ml-2 flex justify-center rounded-md"
            onClick={() => setSettingsModalOpen(true)}
            title="Bot Settings"
          >
            <CogIcon
              aria-label="Settings icon"
              className="size-6  text-white"
              role="img"
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
