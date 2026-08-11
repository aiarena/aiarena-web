import { Link } from "react-router";

import Modal from "@/_components/_actions/Modal";
import SquareButton from "@/_components/_actions/SquareButton";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";

import { AdminCompetition, TrophyCheckResult } from "./adminCompetitionTypes";
import {
  BooleanBadge,
  CompetitionDetail,
  formatDateTime,
  StatusBadge,
} from "./adminCompetitionUtils";
import TrophyStatusMessage from "./TrophyStatusMessage";
import useCompetitionTrophyActions from "./useCompetitionTrophyActions";

interface CompetitionTrophyModalProps {
  competition: AdminCompetition | null;
  checkResult: TrophyCheckResult;
  onCheckResult: (result: TrophyCheckResult) => void;
  onClose: () => void;
  onAwardsGiven: () => void;
}

export default function CompetitionTrophyModal({
  competition,
  checkResult,
  onCheckResult,
  onClose,
  onAwardsGiven,
}: CompetitionTrophyModalProps) {
  const {
    runTrophyCheck,
    runAwardTrophies,
    resetTrophyActions,
    checkInFlight,
    awardInFlight,
    awardMessage,
    awardError,
  } = useCompetitionTrophyActions({
    onCheckResult,
    onAwardsGiven,
  });

  if (!competition) {
    return null;
  }

  const competitionId = getIDFromBase64(competition.id, "CompetitionType");

  const competitionHref = reverseUrl("competition", {
    pk: competitionId,
  });

  const hasRepairableIncorrectTrophies =
    checkResult.status === "incomplete" &&
    (checkResult.incorrectTrophies?.length ?? 0) > 0;

  const canAward =
    checkResult.status === "not_awarded" || hasRepairableIncorrectTrophies;

  const checkDisabled = !competition.awardSet || checkInFlight || awardInFlight;

  const awardDisabled =
    !competition.awardSet || !canAward || checkInFlight || awardInFlight;

  const handleClose = () => {
    resetTrophyActions();
    onClose();
  };

  return (
    <Modal
      isOpen
      onClose={handleClose}
      title={`Manage trophies: ${competition.name}`}
      size="l"
      padding={4}
      paddingX={6}
    >
      <div className="space-y-5 text-white">
        <section className="rounded-sm border border-neutral-700 bg-darken-4 p-4 shadow-lg shadow-black">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            Competition
          </p>

          <Link
            to={competitionHref}
            target="_blank"
            rel="noreferrer"
            className="mt-1 inline-block text-lg font-semibold text-customGreen transition-colors hover:text-white"
          >
            {competition.name}
          </Link>
        </section>

        <section className="rounded-sm border border-neutral-700 bg-darken-4 p-4 shadow-lg shadow-black">
          <dl className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <CompetitionDetail label="Competition ID" value={competitionId} />

            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-gray-400">
                Status
              </dt>

              <dd className="mt-2">
                <StatusBadge status={competition.status} />
              </dd>
            </div>

            <CompetitionDetail
              label="Award set"
              value={competition.awardSet?.name ?? "Not assigned"}
            />

            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-gray-400">
                Awards given
              </dt>

              <dd className="mt-2">
                <BooleanBadge value={competition.awardsGiven} />
              </dd>
            </div>

            <CompetitionDetail
              label="Created"
              value={formatDateTime(competition.dateCreated)}
            />

            <CompetitionDetail
              label="Opened"
              value={formatDateTime(competition.dateOpened)}
            />

            <CompetitionDetail
              label="Closed"
              value={formatDateTime(competition.dateClosed)}
            />
          </dl>
        </section>

        {!competition.awardSet && (
          <div className="rounded-sm border-2 border-orange-500 bg-darken-4 p-4 text-sm text-orange-200 shadow-lg shadow-black">
            <p className="font-semibold">Award set required</p>

            <p className="mt-1 text-gray-300">
              Assign an award set to this competition in the Django admin before
              checking or awarding trophies.
            </p>
          </div>
        )}

        <TrophyStatusMessage result={checkResult} />

        {awardMessage && (
          <div className="rounded-sm border-2 border-customGreen bg-darken-4 p-4 text-sm shadow-lg shadow-black">
            <p className="font-semibold text-customGreen">Trophies awarded</p>

            <p className="mt-1 text-gray-200">{awardMessage}</p>
          </div>
        )}

        {awardError && (
          <div className="rounded-sm border-2 border-red-500 bg-darken-4 p-4 text-sm shadow-lg shadow-black">
            <p className="font-semibold text-red-400">Awarding failed</p>

            <p className="mt-1 text-gray-200">{awardError}</p>
          </div>
        )}

        <section className="rounded-sm border border-neutral-700 bg-darken-4 p-4 shadow-lg shadow-black">
          <div className="grid gap-4 sm:grid-cols-2">
            <SquareButton
              text={checkInFlight ? "Checking Trophies…" : "Check Trophies"}
              onClick={() => runTrophyCheck(competition)}
              isLoading={checkInFlight}
              disabled={checkDisabled}
              color="orange"
              outerClassName="w-full"
              className="min-h-11"
            />

            <SquareButton
              text={
                awardInFlight ? "Awarding Trophies…" : "Award & Fix Trophies"
              }
              onClick={() => runAwardTrophies(competition, checkResult)}
              isLoading={awardInFlight}
              disabled={awardDisabled}
              color="green"
              outerClassName="w-full"
              className="min-h-11"
            />
          </div>

          {!canAward && !competition.awardsGiven && competition.awardSet && (
            <p className="mt-3 text-center text-xs text-gray-400">
              Check the trophies before awarding them.
            </p>
          )}

          {competition.awardsGiven && (
            <p className="mt-3 text-center text-xs text-gray-400">
              Trophy awards have already been recorded for this competition.
            </p>
          )}
        </section>
      </div>
    </Modal>
  );
}
