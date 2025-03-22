// import { useLazyLoadQuery, graphql } from 'react-relay';
// import { nodes } from "@/_lib/relayHelpers";

// export const useCompetitions = (status, first = 10) => {
//   const data = useLazyLoadQuery(
//     graphql`
//       query useCompetitionsQuery($status: CoreCompetitionStatusChoices, $first: Int) {
//         competitions(status: $status, first: $first) {
//           edges {
//             node {
//               id
//               name
//               type
//               dateCreated
//               status
//             }
//           }
//         }
//       }
//     `,
//     { status, first }
//   );
//   return nodes(data.competitions);
// };

import { useLazyLoadQuery, graphql } from "react-relay";
import { nodes } from "@/_lib/relayHelpers";
import { getNodes } from "@/_lib/relayHelpers";
import { useCompetitionsQuery } from "./__generated__/useCompetitionsQuery.graphql";

export const useCompetitions = () => {
  const data = useLazyLoadQuery<useCompetitionsQuery>(
    graphql`
      query useCompetitionsQuery {
        competitions(last: 20) {
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
    {},
  );

  const competitionNodes = getNodes(data.competitions);

  // Transform into a sanitized shape
  return competitionNodes.map((node) => ({
    id: node.id,
    dateCreated: String(node.dateCreated), // Ensure string
    name: node.name || "", // Fallback for title
    type: node.type || "", // Fallback for text
    status: node.status || "", // Convert null to undefined
  }));
};
