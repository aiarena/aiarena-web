import { useLazyLoadQuery, graphql } from "react-relay";
import { getNodes } from "@/_lib/relayHelpers";
import { useNewsQuery } from "./__generated__/useNewsQuery.graphql.js";

export const useNews = () => {
  const data = useLazyLoadQuery<useNewsQuery>(
    graphql`
      query useNewsQuery {
        news(last: 5) {
          edges {
            node {
              id
              title
              text
              created
              ytLink
            }
          }
        }
      }
    `,
    {},
  );

  // Extract and process nodes
  const newsNodes = getNodes(data.news);

  // Transform into a sanitized shape
  return newsNodes.map((node) => ({
    id: node.id,
    created: String(node.created), // Ensure string
    title: node.title || "", // Fallback for title
    text: node.text || "", // Fallback for text
    ytLink: node.ytLink || undefined, // Convert null to undefined
  }));
};
