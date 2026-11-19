import { graphql, useLazyLoadQuery } from "react-relay";
import InformationSection from "./InformationSection";
import { BotQuery } from "./__generated__/BotQuery.graphql";
import { Link, useParams } from "react-router";

import { Suspense, useState } from "react";
import { InformationCircleIcon } from "@heroicons/react/24/outline";
import {
  getBase64FromID,
  getIDFromBase64,
  getNodes,
} from "@/_lib/relayHelpers";
import BotCompetitionsTable from "./BotCompetitionsTable";
import FetchError from "@/_components/_display/FetchError";

import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import BotResults from "./BotResults";
import { reverseUrl } from "@/_lib/reverseUrl"; 
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";

export default function Bot() {
  const { botId } = useParams<{ botId: string }>();
  const [onlyActive, setOnlyActive] = useState(false);
  const [loadResults, setLoadResults] = useState(false);

  const data = useLazyLoadQuery<BotQuery>(
    graphql`
      query BotQuery($id: ID!) {
        node(id: $id) {
          ... on BotType {
            ...InformationSection_bot
            ...BotCompetitionsTable_bot
            botZipUpdated
            activeCompetitions: competitionParticipations(active: true) {
              edges {
                node {
                  id
                }
              }
            }
          }
        }
      }
    `,
    { id: getBase64FromID(botId!, "BotType") || "" },
  );

  if (!data.node) {
    return <FetchError type="bot" />;
  }

  const firstActiveCompetition = getNodes(data.node.activeCompetitions)[0];

  const statsResultsLink = firstActiveCompetition
    ? `${reverseUrl("competition_stats_root", {
        pk: getIDFromBase64(
          firstActiveCompetition.id,
          "CompetitionParticipationType",
        ),
      })}results`
    : undefined;

  return (
    <>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h4 className="mb-4">Bot information</h4>
          <InformationSection bot={data.node} />
        </div>

        <div>
          <h4 className="mb-4">Competition Participations</h4>
          <BotCompetitionsTable
            bot={data.node}
            onlyActive={onlyActive}
            appendHeader={
              <div
                className="flex gap-4 items-center"
                role="group"
                aria-label="Bot filtering controls"
              >
                <div className="flex items-center gap-2">
                  <label
                    htmlFor="downloadable-toggle"
                    className="text-sm font-medium text-gray-300"
                  >
                    Only active
                  </label>
                  <SimpleToggle
                    enabled={onlyActive}
                    onChange={() => setOnlyActive(!onlyActive)}
                  />
                </div>
              </div>
            }
          />
        </div>
      </div>
      <div className="mb-4 mt-8 flex flex-wrap items-center gap-x-4 gap-y-3">
        <h4>Results</h4>

        <div
          role="note"
          className="flex items-center gap-2 rounded-lg border border-neutral-800 bg-darken-2 px-3 py-2 text-sm text-gray-300 shadow-lg shadow-black backdrop-blur"
        >
          <InformationCircleIcon
            aria-hidden="true"
            className="h-5 w-5 shrink-0 text-customGreen"
          />
          <p>
            Competition results are also available on the{" "}
            {statsResultsLink ? (
              <Link
                to={statsResultsLink}
                className="font-semibold text-customGreen hover:text-white"
              >
                Stats page
              </Link>
            ) : (
              <span className="font-semibold text-gray-200">Stats page</span>
            )}
            .
          </p>
        </div>
      </div>
      {!loadResults ? (
        <button
          type="button"
          onClick={() => setLoadResults(true)}
          className="w-full rounded-lg border border-neutral-700 bg-darken-2 px-6 py-5 text-lg font-semibold text-gray-200 shadow-lg shadow-black backdrop-blur transition-colors hover:border-customGreen hover:text-white focus:outline-none focus-visible:border-customGreen"
        >
          Load Bot Results
        </button>
      ) : (
        <Suspense fallback={<DisplaySkeletonTable columns={12} rows={15} />}>
          <BotResults botZipUpdated={data.node.botZipUpdated} />
        </Suspense>
      )}
    </>
  );
}
