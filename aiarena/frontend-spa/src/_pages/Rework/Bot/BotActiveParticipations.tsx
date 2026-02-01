import { graphql, useFragment } from "react-relay";
import { getNodes } from "@/_lib/relayHelpers";
import { BotActiveParticipations_bot$key } from "./__generated__/BotActiveParticipations_bot.graphql";
import BotParticipationCard from "./BotParticipationCard";

type Props = {
  bot: BotActiveParticipations_bot$key;
};

export default function BotActiveParticipations({ bot }: Props) {
  const data = useFragment(
    graphql`
      fragment BotActiveParticipations_bot on BotType {
        activeCompetitions: competitionParticipations(first: 50, active: true) {
          edges {
            node {
              id
              ...BotParticipationCard_bot
            }
          }
        }
      }
    `,
    bot,
  );
  const competitions = getNodes(data.activeCompetitions);
  console.log(data);
  return (
    <div className="grid gap-1">
      <h3 className="col-span-1 text-sm font-semibold tracking-wide text-gray-400 uppercase mb-3">
        Currently competing in
      </h3>
      {competitions.map((comp) => (
        <BotParticipationCard key={comp.id} data={comp} />
      ))}
    </div>
  );
}
