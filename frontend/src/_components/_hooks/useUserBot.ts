import { useLazyLoadQuery, graphql } from 'react-relay';
import { getNodes } from "@/_lib/relayHelpers";
import { useUserBotsQuery } from './__generated__/useUserBotsQuery.graphql';

export const useUserBots = (userId: string | null) => {
  // Always call the query hook, but provide a fallback userId if it's null
  const data = useLazyLoadQuery<useUserBotsQuery>(
    graphql`
      query useUserBotsQuery($userId: ID!) {
        bots(userId: $userId) {
          edges {
            node {
              id    
              name
              created
              type
              url
              botData
              botDataEnabled
              botDataPubliclyDownloadable
              botZip
              botZipPubliclyDownloadable
              botZipUpdated
            }
          }
        }
      }
    `,

    { userId: userId || "default" } // Provide a default placeholder
  );

  // Handle cases where no userId is passed
  if (!userId) {
    console.log("NO USER ID IN REACT HOOK. (useUserBot.ts) - it's okay.")
    return [];
  }

  // Extract nodes and transform them into the required shape
  const botNodes = getNodes(data.bots);
  return botNodes.map((node) => ({
    id: node.id,
    name: node.name || "", // Fallback for title
    created: String(node.created), // Ensure string
    type: node.type || "", // Fallback for type
    url: node.url || "",
    botData: node.botData || "",
    botDataEnabled: node.botDataEnabled || false,
    botDataPubliclyDownloadable: node.botDataPubliclyDownloadable || false,
    botZip: node.botZip || "", 
    botZipPubliclyDownloadable: node. botZipPubliclyDownloadable || false,
    botZipUpdated: node.botZipUpdated || undefined,    
  }));
};
