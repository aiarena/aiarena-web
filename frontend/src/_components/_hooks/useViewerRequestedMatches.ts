import { useLazyLoadQuery, graphql } from "react-relay";
import { getNodes } from "@/_lib/relayHelpers";
import { useViewerRequestedMatchesQuery } from "./__generated__/useViewerRequestedMatchesQuery.graphql";

export interface ViewerRequestedMatch {
  id: string;
  firstStarted: string;
  participant1: {
    id: string;
    name: string;
  } | null;
  participant2: {
    id: string;
    name: string;
  } | null;
  result: {
    type: string;
    winner: { name: string } | null;
  } | null;
}

export const useViewerRequestedMatches = (): ViewerRequestedMatch[] => {
  const data = useLazyLoadQuery<useViewerRequestedMatchesQuery>(
    graphql`
      query useViewerRequestedMatchesQuery {
        viewer {
          requestedMatches {
            edges {
              node {
                id
                firstStarted
                participant1 {
                  id
                  name
                }
                participant2 {
                  id
                  name
                }
                result {
                  type
                  winner {
                    name
                  }
                }
              }
            }
          }
        }
      }
    `,
    {},
  );

  const matchNodes = getNodes(data.viewer?.requestedMatches);

  return matchNodes.map((node) => ({
    id: node.id,
    firstStarted: String(node.firstStarted),
    participant1: node.participant1
      ? { name: node.participant1.name, id: node.participant1.id }
      : null,
    participant2: node.participant2
      ? { name: node.participant2.name, id: node.participant2.id }
      : null,
    result: node.result
      ? {
          type: node.result.type,
          winner: node.result.winner ? { name: node.result.winner.name } : null,
        }
      : null,
  }));
};
