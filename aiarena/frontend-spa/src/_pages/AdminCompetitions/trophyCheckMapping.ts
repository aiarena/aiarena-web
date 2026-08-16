import { TrophyCheckResult } from "./adminCompetitionTypes";

import { useCompetitionTrophyActionsCheckMutation$data } from "./__generated__/useCompetitionTrophyActionsCheckMutation.graphql";

type CheckPayload = NonNullable<
  useCompetitionTrophyActionsCheckMutation$data["checkCompetitionTrophies"]
>;

export function mapTrophyCheckPayload(
  payload: CheckPayload,
): TrophyCheckResult {
  return {
    status: mapGraphQLStatus(payload.status),
    message: payload.message,

    expectedTrophyCount: payload.expectedTrophyCount,

    existingTrophyCount: payload.existingTrophyCount,

    missingTrophyCount: payload.missingTrophyCount,

    incorrectTrophyCount: payload.incorrectTrophyCount,

    incorrectTrophyIds: payload.incorrectTrophyIds ?? [],

    issues: payload.issues ?? [],

    missingTrophies:
      payload.missingTrophies
        ?.filter(
          (trophy): trophy is NonNullable<typeof trophy> => trophy !== null,
        )
        .map((trophy) => ({
          botId: trophy.botId,
          botName: trophy.botName,
          rank: trophy.rank,
          condition: trophy.condition,
          iconId: trophy.iconId,
          iconName: trophy.iconName,
        })) ?? [],

    incorrectTrophies:
      payload.incorrectTrophies
        ?.filter(
          (trophy): trophy is NonNullable<typeof trophy> => trophy !== null,
        )
        .map((trophy) => ({
          id: trophy.id,
          name: trophy.name,

          botId: trophy.botId,
          botName: trophy.botName,

          condition: trophy.condition ?? "",
          conditionDisplay: trophy.conditionDisplay ?? "",

          iconId: trophy.iconId ?? null,
          iconName: trophy.iconName ?? null,
          iconImage: trophy.iconImage ?? null,

          competitionId: trophy.competitionId ?? null,
          competitionName: trophy.competitionName ?? null,

          participated: trophy.participated,
          placement: trophy.placement ?? null,
        })) ?? [],
  };
}

function mapGraphQLStatus(
  status:
    | "INCOMPLETE_OR_INCORRECT"
    | "NOT_AWARDED"
    | "AWARDED"
    | "%future added value"
    | null
    | undefined,
): TrophyCheckResult["status"] {
  switch (status) {
    case "INCOMPLETE_OR_INCORRECT":
      return "incomplete";

    case "NOT_AWARDED":
      return "not_awarded";

    case "AWARDED":
      return "awarded";

    default:
      return "error";
  }
}
