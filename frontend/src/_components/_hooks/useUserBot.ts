import { useLazyLoadQuery, graphql } from 'react-relay';
import { getNodes } from "@/_lib/relayHelpers";
import { useUserBotsQuery } from './__generated__/useUserBotsQuery.graphql';

export const useUserBots = (userId: string) => {
  // Always call the query hook, but provide a fallback userId if it's null
  const data = useLazyLoadQuery<useUserBotsQuery>(
    graphql`
      query useUserBotsQuery($userId: ID!) {
        bots(userId: $userId) {
          edges {
            node {
            ...ProfileBot_bot
            }
          }
        }
      }
    `,

    { userId: userId },
     // Provide a default placeholder
  );

  // Handle cases where no userId is passed
  if (!userId) {
    console.log("No userId.")
    return [];
  }

  // Extract nodes and transform them into the required shape
  const botNodes = getNodes(data.bots);
  return botNodes
};
