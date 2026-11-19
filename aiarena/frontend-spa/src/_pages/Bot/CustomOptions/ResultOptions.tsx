import { CoreMatchParticipationResultChoices } from "../BotResultsTable/__generated__/BotResultsTbody_bot.graphql";

export const resultOptions: {
  id: CoreMatchParticipationResultChoices;
  name: string;
}[] = [
  { id: "NONE", name: "None" },
  { id: "WIN", name: "Win" },
  { id: "LOSS", name: "Loss" },
  { id: "TIE", name: "Tie" },
];
