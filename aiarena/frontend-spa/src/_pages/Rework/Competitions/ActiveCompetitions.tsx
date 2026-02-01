import { graphql, usePaginationFragment } from "react-relay";
import { ActiveCompetitions$key } from "./__generated__/ActiveCompetitions.graphql";
import { getNodes } from "@/_lib/relayHelpers";
import CompetitionCard from "./Competition";
interface ActiveCompetitionsProps {
  data: ActiveCompetitions$key;
}

export default function ActiveCompetitions(props: ActiveCompetitionsProps) {
  const { data } = usePaginationFragment(
    graphql`
      fragment ActiveCompetitions on Query
      @refetchable(queryName: "ActiveCompetitionsPaginationQuery")
      @argumentDefinitions(
        cursor: { type: "String" }
        first: { type: "Int", defaultValue: 50 }
        status: { type: "CoreCompetitionStatusChoices", defaultValue: OPEN }
      ) {
        activeCompetitions: competitions(
          first: $first
          after: $cursor
          status: $status
          orderBy: "-date_created"
        ) @connection(key: "ActiveCompetitionsProps__activeCompetitions") {
          edges {
            node {
              id
              ...CompetitionCard_competition
            }
          }
        }
      }
    `,
    props.data,
  );

  const competitions = getNodes(data?.activeCompetitions);

  return (
    <div className="grid gap-8">
      {competitions.map((comp) => {
        return <CompetitionCard key={comp.id} data={comp} />;
      })}
    </div>
  );
}
