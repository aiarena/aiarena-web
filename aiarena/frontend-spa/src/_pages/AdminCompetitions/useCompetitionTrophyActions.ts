import { useState } from "react";
import { graphql, useMutation } from "react-relay";

import { AdminCompetition, TrophyCheckResult } from "./adminCompetitionTypes";
import { mapTrophyCheckPayload } from "./trophyCheckMapping";

import { useCompetitionTrophyActionsAwardMutation } from "./__generated__/useCompetitionTrophyActionsAwardMutation.graphql";
import { useCompetitionTrophyActionsCheckMutation } from "./__generated__/useCompetitionTrophyActionsCheckMutation.graphql";

interface UseCompetitionTrophyActionsProps {
  onCheckResult: (result: TrophyCheckResult) => void;
  onAwardsGiven: () => void;
}

export default function useCompetitionTrophyActions({
  onCheckResult,
  onAwardsGiven,
}: UseCompetitionTrophyActionsProps) {
  const [awardMessage, setAwardMessage] = useState<string | null>(null);
  const [awardError, setAwardError] = useState<string | null>(null);

  const [commitCheck, checkInFlight] =
    useMutation<useCompetitionTrophyActionsCheckMutation>(graphql`
      mutation useCompetitionTrophyActionsCheckMutation(
        $input: CheckCompetitionTrophiesInput!
      ) {
        checkCompetitionTrophies(input: $input) {
          status
          message
          awardsGiven

          expectedTrophyCount
          existingTrophyCount
          missingTrophyCount
          incorrectTrophyCount

          incorrectTrophyIds
          issues

          missingTrophies {
            botId
            botName
            rank
            condition
            iconId
            iconName
          }

          incorrectTrophies {
            id
            name

            botId
            botName

            condition
            conditionDisplay

            iconId
            iconName
            iconImage

            competitionId
            competitionName

            participated
            placement
          }

          errors {
            field
            messages
          }
        }
      }
    `);

  const [commitAward, awardInFlight] =
    useMutation<useCompetitionTrophyActionsAwardMutation>(graphql`
      mutation useCompetitionTrophyActionsAwardMutation(
        $input: AwardCompetitionTrophiesInput!
      ) {
        awardCompetitionTrophies(input: $input) {
          success
          message

          awardsGiven

          createdTrophyCount
          deletedTrophyCount

          createdTrophyIds
          deletedTrophyIds

          errors {
            field
            messages
          }
        }
      }
    `);

  const resetTrophyActions = () => {
    setAwardMessage(null);
    setAwardError(null);
  };

  const runTrophyCheck = (competition: AdminCompetition) => {
    resetTrophyActions();

    onCheckResult({
      status: "loading",
    });

    commitCheck({
      variables: {
        input: {
          competition: competition.id,
        },
      },

      onCompleted: (response) => {
        const payload = response.checkCompetitionTrophies;

        if (!payload) {
          onCheckResult({
            status: "error",
            message: "The server returned no trophy-check result.",
          });
          return;
        }

        const mutationErrors =
          payload.errors?.flatMap((error) => error?.messages ?? []) ?? [];

        if (mutationErrors.length > 0) {
          onCheckResult({
            status: "error",
            message: mutationErrors.join(" "),
          });
          return;
        }

        onCheckResult(mapTrophyCheckPayload(payload));
      },

      onError: (error) => {
        onCheckResult({
          status: "error",
          message: error.message,
        });
      },
    });
  };

  const runAwardTrophies = (
    competition: AdminCompetition,
    checkResult: TrophyCheckResult,
  ) => {
    resetTrophyActions();

    commitAward({
      variables: {
        input: {
          competition: competition.id,
        },
      },

      updater: (store) => {
        store.invalidateStore();
      },

      onCompleted: (response) => {
        const payload = response.awardCompetitionTrophies;

        if (!payload) {
          setAwardError("The server returned no trophy-award result.");
          return;
        }

        const mutationErrors =
          payload.errors?.flatMap((error) => error?.messages ?? []) ?? [];

        if (mutationErrors.length > 0) {
          setAwardError(mutationErrors.join(" "));
          return;
        }

        if (!payload.success) {
          setAwardError(payload.message ?? "Trophies could not be awarded.");
          return;
        }

        const createdCount = payload.createdTrophyCount ?? 0;
        const deletedCount = payload.deletedTrophyCount ?? 0;

        setAwardMessage(
          `${payload.message} Created ${createdCount} and removed ${deletedCount}.`,
        );

        onCheckResult({
          status: "awarded",
          message: "Trophies have been awarded.",

          expectedTrophyCount: checkResult.expectedTrophyCount ?? 0,
          existingTrophyCount: checkResult.expectedTrophyCount ?? 0,

          missingTrophyCount: 0,
          incorrectTrophyCount: 0,

          missingTrophies: [],
          incorrectTrophyIds: [],
          incorrectTrophies: [],
          issues: [],
        });

        onAwardsGiven();
      },

      onError: (error) => {
        setAwardError(error.message);
      },
    });
  };

  return {
    runTrophyCheck,
    runAwardTrophies,
    resetTrophyActions,

    checkInFlight,
    awardInFlight,

    awardMessage,
    awardError,
  };
}
