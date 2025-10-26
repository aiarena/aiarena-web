import { graphql, useFragment } from "react-relay";
import { CompetitionCard_competition$key } from "./__generated__/CompetitionCard_competition.graphql";

interface CompetitionProps {
  key: string;
  data: CompetitionCard_competition$key;
}

export default function CompetitionCard(props: CompetitionProps) {
  const competition = useFragment(
    graphql`
      fragment CompetitionCard_competition on CompetitionType {
        id
        name
      }
    `,
    props.data
  );
  return <div key={props.key}>Competition {competition.name}</div>;
}
