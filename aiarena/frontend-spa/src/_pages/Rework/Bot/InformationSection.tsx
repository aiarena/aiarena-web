import { graphql, useFragment } from "react-relay";
import type { InformationSection_bot$key } from "./__generated__/InformationSection_bot.graphql";
import clsx from "clsx";
import { useState } from "react";
import { TrophyIcon } from "@heroicons/react/24/outline";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import BotTrophiesModal from "@/_pages/UserBots/UserBotsSection/_modals/BotTrophiesModal";
import { MarkdownDisplay } from "@/_components/_actions/MarkdownDisplay";
import { ArrowDownCircleIcon } from "@heroicons/react/20/solid";
import { getDateTimeISOString } from "@/_lib/dateUtils";
import RenderCodeLanguage from "@/_components/_display/RenderCodeLanguage";
import { RenderRace } from "@/_components/_display/RenderRace";
import BotActiveParticipations from "./BotActiveParticipations";

interface InformationSectionProps {
  bot: InformationSection_bot$key;
}

export default function InformationSection({ bot }: InformationSectionProps) {
  const [isTrophiesModalOpen, setTrophiesModalOpen] = useState(false);
  const data = useFragment(
    graphql`
      fragment InformationSection_bot on BotType {
        id
        name
        playsRace {
          name
          label
          id
        }
        created
        type
        botZip
        botZipUpdated
        botZipPubliclyDownloadable
        botData
        botDataEnabled
        botDataPubliclyDownloadable
        wikiArticle
        trophies {
          edges {
            node {
              name
              trophyIconImage
              trophyIconName
            }
          }
        }
        ...BotTrophiesModal_bot
        ...BotActiveParticipations_bot

        user {
          username
          id
        }
      }
    `,
    bot,
  );

  const hasBotZip = !!data.botZip;
  const hasBotData = !!data.botData && data.botDataEnabled;

  const lastUpdated = data.botZipUpdated ?? data.created;

  return (
    <section aria-labelledby="bot-information-heading" className="mb-8">
      <div
        className={clsx(
          "rounded-2xl border border-neutral-800 bg-darken-2",
          "shadow-lg shadow-black p-6 sm:p-8",
        )}
      >
        <div className="items-baseline gap-2 mb-6">
          <div className="flex">
            <h2
              id="bot-information-heading"
              className="text-xl sm:text-2xl font-semibold text-white"
            >
              {data.name}
            </h2>
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
                {getNodes(data?.trophies).length || 0}
              </span>
            </div>
          </div>
          {data.user?.username && (
            <p className="text-sm text-gray-300 ml-4">
              by{" "}
              <span className="font-medium text-gray-100">
                <a
                  href={`/authors/${getIDFromBase64(data.user.id, "UserType")}`}
                >
                  {data.user.username}
                </a>
              </span>
            </p>
          )}
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:border-r border-neutral-700">
            <h3 className="col-span-1 text-sm font-semibold tracking-wide text-gray-400 uppercase mb-3">
              Details
            </h3>
            <dl className="space-y-2 text-sm sm:text-base p-4">
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Race</dt>
                <dd className="flex-1 text-gray-100">
                  <RenderRace race={data?.playsRace} />
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Type</dt>
                <dd className="flex-1 text-gray-100">
                  <RenderCodeLanguage type={`${data.type || "--"}`} />
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Created</dt>
                <dd className="flex-1 text-gray-100">
                  {getDateTimeISOString(data.created) || "--"}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Last Updated</dt>
                <dd className="flex-1 text-gray-100">
                  {getDateTimeISOString(lastUpdated) || "--"}
                </dd>
              </div>

              <hr className="border-neutral-700 my-3" />

              <div className="flex items-center mb-4">
                <dt className="w-32 text-gray-400">Bot Zip</dt>
                <dd className="flex-1 text-gray-100">
                  {data.botZipPubliclyDownloadable ? (
                    <>
                      {hasBotZip ? (
                        <a href={data.botZip} download="" className="text-sm">
                          <span className="flex gap-1">
                            <ArrowDownCircleIcon height={18} /> Download
                          </span>
                        </a>
                      ) : (
                        <span className="text-gray-300">No Zip Available</span>
                      )}{" "}
                    </>
                  ) : (
                    <span className="text-gray-300">Private</span>
                  )}
                </dd>
              </div>

              <div className="flex items-center mb-4">
                <dt className="w-32 text-gray-400">Bot Data</dt>
                <dd className="flex-1 text-gray-100">
                  {data.botDataPubliclyDownloadable ? (
                    <>
                      {hasBotData ? (
                        <a href={data.botData} download="" className="text-sm">
                          <span className="flex gap-1">
                            <ArrowDownCircleIcon height={18} /> Download
                          </span>
                        </a>
                      ) : (
                        <span className="text-gray-300">No Data Available</span>
                      )}
                    </>
                  ) : (
                    <span className="text-gray-300">Private</span>
                  )}
                </dd>
              </div>
            </dl>
            <BotActiveParticipations bot={data} />
          </div>

          <div className="col-span-2">
            <h3 className=" text-sm font-semibold tracking-wide text-gray-400 uppercase mb-3">
              Biography
            </h3>
            {data.wikiArticle ? (
              <div className="prose prose-invert max-w-none text-sm sm:text-base">
                <MarkdownDisplay markdown={data.wikiArticle} />
              </div>
            ) : (
              <p className="text-sm text-gray-400">
                No biography has been added for this bot yet.
              </p>
            )}
          </div>
        </div>
      </div>

      {isTrophiesModalOpen && (
        <BotTrophiesModal
          bot={data}
          isOpen={isTrophiesModalOpen}
          onClose={() => setTrophiesModalOpen(false)}
          noItemsMessage={`${data.name} doesn't own any trophies.`}
        />
      )}
    </section>
  );
}
