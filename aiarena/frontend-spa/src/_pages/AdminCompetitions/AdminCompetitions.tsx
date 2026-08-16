import { useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Link } from "react-router";

import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";

import CompetitionTrophyModal from "./CompetitionTrophyModal";
import { AdminCompetition, TrophyCheckResult } from "./adminCompetitionTypes";

import { AdminCompetitionsQuery } from "./__generated__/AdminCompetitionsQuery.graphql";
import { StatusBadge } from "./utils/StatusBadge.";
import { DateValue } from "./utils/DateValue";

const EMPTY_CHECK_RESULT: TrophyCheckResult = {
  status: "idle",
};

export default function AdminCompetitions() {
  const data = useLazyLoadQuery<AdminCompetitionsQuery>(
    graphql`
      query AdminCompetitionsQuery {
        competitions(first: 100, orderBy: "-date_created") {
          edges {
            node {
              id
              name
              status
              dateCreated
              dateOpened
              dateClosed
              awardsGiven
              awardSet {
                id
                name
              }
            }
          }
        }
      }
    `,
    {},
    {
      fetchPolicy: "network-only",
    },
  );

  const [selectedCompetition, setSelectedCompetition] =
    useState<AdminCompetition | null>(null);

  const [checkResult, setCheckResult] =
    useState<TrophyCheckResult>(EMPTY_CHECK_RESULT);

  const competitions: AdminCompetition[] =
    data.competitions?.edges
      ?.map((edge) => edge?.node)
      .filter(
        (competition): competition is AdminCompetition =>
          competition !== null && competition !== undefined,
      ) ?? [];

  const openModal = (competition: AdminCompetition) => {
    setSelectedCompetition(competition);
    setCheckResult(EMPTY_CHECK_RESULT);
  };

  const closeModal = () => {
    setSelectedCompetition(null);
    setCheckResult(EMPTY_CHECK_RESULT);
  };

  const markSelectedCompetitionAwarded = () => {
    if (!selectedCompetition) {
      return;
    }

    setSelectedCompetition({
      ...selectedCompetition,
      awardsGiven: new Date().toISOString(),
    });
  };

  if (!data.competitions) {
    return (
      <div className="rounded-xl border border-neutral-800 bg-darken-2 p-6 shadow-lg backdrop-blur-lg">
        <p className="text-center text-neutral-300">
          You do not have permission to manage competitions.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-hidden rounded-xl border border-neutral-800 bg-darken-2 shadow-lg backdrop-blur-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="border-b border-neutral-800 bg-neutral-900/40">
              <tr>
                <th className="px-5 py-4 text-sm font-semibold text-neutral-200">
                  Competition
                </th>

                <th className="px-5 py-4 text-sm font-semibold text-neutral-200">
                  Status
                </th>

                <th className="px-5 py-4 text-sm font-semibold text-neutral-200">
                  Created
                </th>

                <th className="px-5 py-4 text-sm font-semibold text-neutral-200">
                  Closed
                </th>

                <th className="px-5 py-4 text-sm font-semibold text-neutral-200">
                  Award set
                </th>

                <th className="px-5 py-4 text-sm font-semibold text-neutral-200">
                  Awards given
                </th>

                <th className="px-5 py-4 text-right text-sm font-semibold text-neutral-200">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-neutral-800">
              {competitions.map((competition) => {
                const competitionId = getIDFromBase64(
                  competition.id,
                  "CompetitionType",
                );

                const competitionHref = reverseUrl("competition", {
                  pk: competitionId,
                });

                return (
                  <tr
                    key={competition.id}
                    className="transition-colors hover:bg-neutral-900/30"
                  >
                    <td className="px-5 py-4">
                      <Link
                        to={competitionHref}
                        className="font-medium text-neutral-100 hover:text-white hover:underline"
                      >
                        {competition.name}
                      </Link>

                      <div className="mt-1 text-xs text-neutral-500">
                        ID: {competitionId}
                      </div>
                    </td>

                    <td className="px-5 py-4">
                      <StatusBadge status={competition.status} />
                    </td>

                    <td className="whitespace-nowrap px-5 py-4 text-sm text-neutral-300">
                      <DateValue value={competition.dateCreated} />
                    </td>

                    <td className="whitespace-nowrap px-5 py-4 text-sm text-neutral-300">
                      <DateValue value={competition.dateClosed} />
                    </td>

                    <td className="px-5 py-4 text-sm text-neutral-300">
                      {competition.awardSet?.name ?? (
                        <span className="text-neutral-500">No award set</span>
                      )}
                    </td>

                    <td className="whitespace-nowrap px-5 py-4 text-sm text-neutral-300">
                      {competition.awardsGiven ? (
                        <DateValue value={competition.awardsGiven} />
                      ) : (
                        <span className="text-neutral-500">Not awarded</span>
                      )}
                    </td>

                    <td className="px-5 py-4 text-right">
                      <button
                        type="button"
                        onClick={() => openModal(competition)}
                        className="rounded-lg border border-neutral-700 bg-neutral-800 px-4 py-2 text-sm font-medium text-neutral-100 transition-colors hover:border-neutral-600 hover:bg-neutral-700"
                      >
                        Manage
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {competitions.length === 0 && (
          <div className="p-8 text-center text-neutral-400">
            No competitions found.
          </div>
        )}
      </div>

      <CompetitionTrophyModal
        competition={selectedCompetition}
        checkResult={checkResult}
        onCheckResult={setCheckResult}
        onClose={closeModal}
        onAwardsGiven={markSelectedCompetitionAwarded}
      />
    </>
  );
}
