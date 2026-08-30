import { graphql, useLazyLoadQuery } from "react-relay";
import InformationSection from "./InformationSection";
import { BotQuery } from "./__generated__/BotQuery.graphql";
import { Link, useParams } from "react-router";

import { Suspense, useState } from "react";
import {
  getBase64FromID,
  getIDFromBase64,
  getNodes,
} from "@/_lib/relayHelpers";
import BotCompetitionsTable from "./BotCompetitionsTable";
import FetchError from "@/_components/_display/FetchError";

import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import BotResults from "./BotResults";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import { reverseUrl } from "@/_lib/reverseUrl";

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
      <div className="mb-4 mt-8 flex gap-4 break-words items-baseline align-baseline">
        <h4>Results</h4>

        <p className="text-sm text-gray-300">
          * Match Result from competitions are also available at:{" "}
          {statsResultsLink ? (
            <Link
              to={statsResultsLink}
              className="font-medium text-customGreen hover:text-white"
            >
              Stats Page
            </Link>
          ) : (
            <span>Stats Page</span>
          )}{" "}
          — it supports all sorts.
        </p>
      </div>
      {!loadResults ? (
        <div className="flex flex-col items-start gap-3">
          <button
            type="button"
            onClick={() => setLoadResults(true)}
            className="rounded-lg border border-neutral-700 bg-neutral-900 px-4 py-2 font-semibold text-gray-200 transition hover:border-customGreen"
          >
            Load Bot Results
          </button>
        </div>
      ) : (
        <Suspense
          fallback={
            <DisplaySkeleton height={800} styles={SkeletonCardShadow} />
          }
        >
          <BotResults botZipUpdated={data.node.botZipUpdated} />
        </Suspense>
      )}
    </>
  );
}
