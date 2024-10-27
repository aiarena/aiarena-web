import { useLazyLoadQuery, graphql } from 'react-relay';
import { nodes } from "@/_lib/relayHelpers";

export const useBots = (name = '', last = 5) => {
  const data = useLazyLoadQuery(
    graphql`
      query useBotsQuery($name: String, $first: Int) {
        bots(name: $name, first: $first) {
          edges {
            node {
              id    
              name
              created
              type
              user {
                id
                username
              }
            }
          }
        }
      }
    `,
    { name, last }
  );
  return nodes(data.bots);
};
