import { useLazyLoadQuery, graphql } from "react-relay";
import { getNodes } from "@/_lib/relayHelpers";
import { useBotsQuery } from "./__generated__/useBotsQuery.graphql";

export const useBots = (name = "") => {
  const data = useLazyLoadQuery<useBotsQuery>(
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
    { name },
  );
  //   return nodes(data.bots);
  // };

  const botNodes = getNodes(data.bots);

  // Transform into a sanitized shape
  return botNodes.map((node) => ({
    id: node.id,
    created: String(node.created), // Ensure string
    name: node.name || "", // Fallback for title
    type: node.type || "", // Fallback for text
    user: {
      id: node.user.id,
      username: node.user.username,
    },
  }));
};
