import { graphql, useLazyLoadQuery } from "react-relay";
import { CompetitionParticipationStatsQuery } from "./__generated__/CompetitionParticipationStatsQuery.graphql";
import MapStatsTable from "./MapStatsTable";
import MatchupStatsTable from "./MatchupStatsTable";
import { getBase64FromID } from "@/_lib/relayHelpers";

interface CompetitionParticipationStatsProps {
  id: string;
}

export default function CompetitionParticipationStats(
  props: CompetitionParticipationStatsProps
) {
  const data = useLazyLoadQuery<CompetitionParticipationStatsQuery>(
    graphql`
      query CompetitionParticipationStatsQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionParticipationType {
            id
            bot {
              id
              name
            }
            competition {
              id
              name
            }
            elo
            ...MapStatsTable_node
            ...MatchupStatsTable_node
          }
        }
      }
    `,
    { id: getBase64FromID(props.id!, "CompetitionParticipationType") || "" }
  );

  if (!data.node) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Competition participation not found</p>
      </div>
    );
  }

  const participation = data.node;

  return (
    <div className="space-y-8">
      <div className="divider">
        <span></span>
        <span>
          <h2 className="text-2xl font-semibold">
            {participation.bot?.name} - {participation.competition?.name} stats
          </h2>
        </span>
        <span></span>
      </div>

      <MapStatsTable data={participation} />

      <MatchupStatsTable data={participation} />
    </div>
  );
}
