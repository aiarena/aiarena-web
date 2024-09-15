import { useLazyLoadQuery, graphql } from 'react-relay';
import { nodes } from "@/_lib/relayHelpers";

export const useCompetitions = (status, first = 10) => {
  const data = useLazyLoadQuery(
    graphql`
      query useCompetitionsQuery($status: CoreCompetitionStatusChoices, $first: Int) {
        competitions(status: $status, first: $first) {
          edges {
            node {
              id
              name
              type
              dateCreated
              status
            }
          }
        }
      }
    `,
    { status, first }
  );
  return nodes(data.competitions);
};
