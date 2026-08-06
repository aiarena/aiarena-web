import { AdminCompetitionsQuery } from "./__generated__/AdminCompetitionsQuery.graphql";

type CompetitionEdge = NonNullable<
  NonNullable<AdminCompetitionsQuery["response"]["competitions"]>["edges"]
>[number];

export type AdminCompetition = NonNullable<
  NonNullable<CompetitionEdge>["node"]
>;

export type TrophyCheckStatus =
  | "idle"
  | "loading"
  | "incomplete"
  | "not_awarded"
  | "awarded"
  | "error";

export type ExpectedTrophy = {
  readonly botId: string;
  readonly botName: string;
  readonly rank: number;
  readonly condition: string;
  readonly iconId: string;
  readonly iconName: string;
};

export type IncorrectTrophy = {
  readonly id: string;
  readonly name: string;

  readonly botId: string;
  readonly botName: string;

  readonly condition: string;
  readonly conditionDisplay: string;

  readonly iconId: string | null;
  readonly iconName: string | null;
  readonly iconImage: string | null;

  readonly competitionId: string;
  readonly competitionName: string;

  readonly participated: boolean;
  readonly placement: number | null;
};

export type TrophyCheckResult = {
  status: TrophyCheckStatus;
  message?: string | null;

  expectedTrophyCount?: number;
  existingTrophyCount?: number;
  missingTrophyCount?: number;
  incorrectTrophyCount?: number;

  missingTrophies?: readonly ExpectedTrophy[];

  incorrectTrophyIds?: readonly string[];
  incorrectTrophies?: readonly IncorrectTrophy[];

  issues?: readonly string[];
};
