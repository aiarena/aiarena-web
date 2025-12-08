import { useState } from "react";
import { graphql, useFragment } from "react-relay";
import { getDateToLocale } from "@/_lib/dateUtils";
import BotSettingsModal from "../../../_pages/UserBots/UserBotsSection/_modals/bot_settings_modal/BotSettingsModal";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import BotTrophiesModal from "../../../_pages/UserBots/UserBotsSection/_modals/BotTrophiesModal";
import { TrophyIcon, PencilIcon } from "@heroicons/react/20/solid";
import { UserBotHeader_bot$key } from "./__generated__/UserBotHeader_bot.graphql";
import RenderCodeLanguage from "../RenderCodeLanguage";

export interface UserBotHeaderProps {
  bot: UserBotHeader_bot$key;
}

export default function UserBotHeader(props: UserBotHeaderProps) {
  const bot = useFragment(
    graphql`
      fragment UserBotHeader_bot on BotType {
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

  return (
    <div className="p-4 border-b border-gray-800 bg-[linear-gradient(240deg,rgb(0,0,0,0.3)_0%,rgba(0,0,0,0.9)_100%)]  rounded-t-lg">
      <div className="text-left space-y-2">
        <div className="flex justify-between flsex-wrap">
          <div className="flex items-center flex-wrap">
            {/* Bot Name */}
            <a
              href={`/bots/${getIDFromBase64(bot.id, "BotType")}`}
              className="text-lg text-customGreen font-medium"
            >
              {bot.name}
            </a>

            <div
              className="flex items-center cursor-pointer hover:bg-neutral-800 rounded p-1 ml-2 border border-transparent hover:border-neutral-700"
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
            className="cursor-pointer hover:bg-neutral-800 hover:border-neutral-500 py-1 px-2 ml-2 flex justify-center rounded-md gap-2 border border-neutral-600 items-center shadow-sm shadow-black"
            onClick={() => setSettingsModalOpen(true)}
            title="Bot Settings"
          >
            Edit Bot
            <PencilIcon
              aria-label="Settings icon"
              className="size-5  text-white"
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
              <p className="text-sm text-gray-400 flex gap-2">
                <span className="font-bold">Type:</span>
                <RenderCodeLanguage type={`${bot.type}`} />
              </p>
            )}
            {bot.botZipUpdated && (
              <p className="text-sm text-gray-400">
                <span className="font-bold">Zip Updated:</span>{" "}
                {getDateToLocale(bot.botZipUpdated)}
              </p>
            )}
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
