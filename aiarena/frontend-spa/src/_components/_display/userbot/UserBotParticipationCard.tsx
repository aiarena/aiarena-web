import { graphql, useFragment } from "react-relay";
import { Link } from "react-router";
import clsx from "clsx";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
import { getDotColor } from "@/_lib/getDotColor";
import { statsSideNavbarLinks } from "@/_pages/Rework/CompetitionParticipation/StatsSideNavbarLinks";
import ActiveDot from "../ActiveDot";
import EloTrendIcon from "../EloTrendIcon";
import ResultSplitBar from "../ResultSplitBar";
import { UserBotParticipationCard_participation$key } from "./__generated__/UserBotParticipationCard_participation.graphql";

interface UserBotParticipationCardProps {
  participation: UserBotParticipationCard_participation$key;
}

export default function UserBotParticipationCard(
  props: UserBotParticipationCardProps,
) {
  const participation = useFragment(
    graphql`
      fragment UserBotParticipationCard_participation on CompetitionParticipationType {
        id
        active
        competition {
          id
          name
          status
        }
        elo
        trend
        highestElo
        divisionNum
        matchCount
        winCount
        winPerc
        tieCount
        tiePerc
        lossCount
        lossPerc
        crashCount
        crashPerc
      }
    `,
    props.participation,
  );

  const participationPk = getIDFromBase64(
    participation.id,
    "CompetitionParticipationType",
  );
  const atPeak =
    participation.highestElo != null &&
    participation.elo >= participation.highestElo;
  const hasCrashes = participation.crashCount > 0;

  return (
    <article className="rounded-xl border border-neutral-700 p-4 shadow-lg shadow-black space-y-4">
      {/* Header: competition + division, then elo + peak */}
      <header className="min-w-0 space-y-2 border-b border-neutral-700 pb-3">
        <div className="flex flex-wrap items-center gap-2">
          <div
            title={`Competition Status: ${participation.competition.status} \nParticipating: ${participation.active ? "Yes" : "No"}`}
          >
            <ActiveDot
              color={getDotColor(
                participation.active,
                participation.competition.status ?? "",
              )}
            />
          </div>
          <Link
            to={reverseUrl("competition", {
              pk: getIDFromBase64(
                participation.competition.id,
                "CompetitionType",
              ),
            })}
            className="truncate text-base font-semibold"
          >
            {participation.competition.name}
          </Link>
          <span className="rounded-full border border-neutral-600 bg-neutral-800 px-2 py-0.5 text-xs font-medium text-gray-100">
            {participation.divisionNum == 0
              ? "Placements"
              : `Division ${participation.divisionNum}`}
          </span>
        </div>
        <dl className="flex flex-wrap items-end gap-x-6 gap-y-2">
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-gray-400">
              Elo
            </dt>
            <dd className="flex items-center gap-1.5 text-lg font-semibold leading-tight tabular-nums text-white">
              {participation.elo}
              {participation.active && participation.trend != null && (
                <EloTrendIcon trend={participation.trend} size={18} />
              )}
            </dd>
          </div>
          <div className="border-l border-neutral-700 pl-6">
            <dt className="text-xs font-semibold uppercase tracking-wide text-gray-400">
              Peak
            </dt>
            <dd className="text-base leading-tight tabular-nums text-gray-200">
              {atPeak ? (
                <span className="inline-block rounded-full border border-customGreen/50 bg-customGreen/10 px-2 py-0.5 text-xs font-medium text-customGreen">
                  At peak
                </span>
              ) : (
                (participation.highestElo ?? "—")
              )}
            </dd>
          </div>
        </dl>
      </header>

      {/* Record */}
      <div className="grid gap-4 sm:grid-cols-[1fr_auto] sm:items-center">
        <div className="space-y-1.5">
          <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 text-sm tabular-nums">
            <span className="text-gray-300">
              <span className="font-semibold text-white">
                {participation.matchCount}
              </span>{" "}
              matches
            </span>
            <span className="text-customGreen">
              {participation.winPerc.toFixed(1)}% W
            </span>
            <span className="text-gray-300">
              {participation.tiePerc.toFixed(1)}% T
            </span>
            <span className="text-red-400">
              {participation.lossPerc.toFixed(1)}% L
            </span>
          </div>
          <ResultSplitBar
            winPerc={participation.winPerc}
            tiePerc={participation.tiePerc}
            lossPerc={participation.lossPerc}
          />
          <span className="text-xs tabular-nums text-gray-300">
            {participation.winCount}W · {participation.tieCount}T ·{" "}
            {participation.lossCount}L
          </span>
        </div>

        <div
          className={clsx(
            "flex items-center gap-2 sm:justify-end",
            hasCrashes ? "text-red-400" : "text-gray-300",
          )}
        >
          <ExclamationTriangleIcon className="size-4" aria-hidden />
          <span className="text-sm">
            <span className="font-semibold tabular-nums">
              {participation.crashCount}
            </span>{" "}
            {participation.crashCount === 1 ? "crash" : "crashes"}
            {hasCrashes && (
              <span className="text-gray-300">
                {" "}
                ({participation.crashPerc.toFixed(1)}%)
              </span>
            )}
          </span>
        </div>
      </div>

      {/* Quicklinks into the participation stats pages */}
      <nav
        aria-label={`${participation.competition.name} stats`}
        className="flex flex-wrap gap-2"
      >
        {statsSideNavbarLinks.map((link) => (
          <Link
            key={link.state}
            to={reverseUrl(`competition_stats_${link.state}`, {
              pk: participationPk,
            })}
            className="rounded-full border border-neutral-600 bg-neutral-800 px-3 py-1 text-sm font-medium text-gray-100 transition-colors hover:border-customGreen hover:text-white"
          >
            {link.name}
          </Link>
        ))}
      </nav>
    </article>
  );
}
