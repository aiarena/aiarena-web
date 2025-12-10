import { graphql, useFragment } from "react-relay";
import clsx from "clsx";
import { MarkdownDisplay } from "@/_components/_actions/MarkdownDisplay";
import { getDateTimeISOString } from "@/_lib/dateUtils";
import { CompetitionInformationSection_competition$key } from "./__generated__/CompetitionInformationSection_competition.graphql";
import { ArrowDownCircleIcon } from "@heroicons/react/20/solid";
import { useState } from "react";
import CompetitionRoundsModal from "./_modals/CompetitionRoundsModal";
import MutedButton from "@/_components/_actions/MutedButton";

interface CompetitionInformationSectionProps {
  competiton: CompetitionInformationSection_competition$key;
}

export default function CompetitionInformationSection({
  competiton,
}: CompetitionInformationSectionProps) {
  const [isRoundsModalOpen, setIsRoundsModalOpen] = useState(false);

  const data = useFragment(
    graphql`
      fragment CompetitionInformationSection_competition on CompetitionType {
        ...CompetitionRoundsModal_competition
        wikiArticle
        id
        name
        dateClosed
        dateCreated
        dateOpened
        game
        gameMode
        maps {
          edges {
            node {
              downloadLink
              enabled
              id
              name
            }
          }
          totalCount
        }
        status
      }
    `,
    competiton
  );

  return (
    <section aria-labelledby="bot-information-heading" className="mb-8">
      <div
        className={clsx(
          "rounded-2xl border border-neutral-800 bg-darken-2",
          "shadow-lg shadow-black p-6 sm:p-8"
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
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:border-r border-neutral-700">
            <h3 className="col-span-1 text-sm font-semibold tracking-wide text-gray-400 uppercase mb-3">
              Details
            </h3>
            <dl className="space-y-2 text-sm sm:text-base p-4">
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Game</dt>
                <dd className="flex-1 text-gray-100">{data.game || "--"}</dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Game Mode</dt>
                <dd className="flex-1 text-gray-100">
                  {data.gameMode || "--"}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Created</dt>
                <dd className="flex-1 text-gray-100">
                  {getDateTimeISOString(data.dateCreated) || "--"}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Opened</dt>
                <dd className="flex-1 text-gray-100">
                  {getDateTimeISOString(data.dateOpened) || "--"}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Closed</dt>
                <dd className="flex-1 text-gray-100">
                  {getDateTimeISOString(data.dateClosed) || "--"}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-32 text-gray-400">Status</dt>
                <dd className="flex-1 text-gray-100 font-bold">
                  {data.status}
                </dd>
              </div>
              <div className="flex gap-2 justify-center">
                <span className="flex-1 text-gray-100 font-bold my-2">
                  <MutedButton
                    title="View Rounds"
                    onClick={() => setIsRoundsModalOpen(true)}
                  >
                    View Rounds
                  </MutedButton>
                </span>
              </div>

              <hr className="border-neutral-700 my-3" />

              <div>
                <span className="w-32 text-gray-400 flex">Maps</span>
                <ul className="ml-4 mt-2 inline-block ">
                  {data.maps?.totalCount && data.maps?.totalCount >= 0 ? (
                    <>
                      {data.maps.edges.map((map) => (
                        <li key={map?.node?.id} className="text-gray-100 ">
                          <a
                            href={`${map?.node?.downloadLink}`}
                            className="flex gap-1 items-center"
                          >
                            <ArrowDownCircleIcon height={18} />{" "}
                            {map?.node?.name}
                          </a>
                        </li>
                      ))}
                    </>
                  ) : (
                    <p>No maps</p>
                  )}
                </ul>
              </div>
            </dl>
          </div>

          <div className="col-span-2">
            <h3 className=" text-sm font-semibold tracking-wide text-gray-400 uppercase mb-3">
              Information
            </h3>
            {data.wikiArticle ? (
              <div className="prose prose-invert max-w-none text-sm sm:text-base">
                <MarkdownDisplay markdown={data.wikiArticle} />
              </div>
            ) : (
              <p className="text-sm text-gray-400">
                No information has been added for this competition.
              </p>
            )}
          </div>
        </div>
      </div>
      {isRoundsModalOpen && (
        <CompetitionRoundsModal
          competition={data}
          isOpen={isRoundsModalOpen}
          onClose={() => setIsRoundsModalOpen(false)}
        />
      )}
    </section>
  );
}
