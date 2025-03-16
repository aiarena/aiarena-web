import { useLazyLoadQuery, graphql } from 'react-relay';
import { getNodes, nodes } from "@/_lib/relayHelpers";

import { getDataIDsFromFragment } from 'relay-runtime';
import { useBotQuery } from './__generated__/useBotQuery.graphql';

export const useBot = (botId: string) => {
    console.log("attempting to get bot with," , botId)
  const data = useLazyLoadQuery<useBotQuery>(
    graphql`
      query useBotQuery($id: ID!) {
        node(id: $id) {
          ...on BotType{
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
    `,
    { id: botId }
  );




const bot = data.node;
if (!bot || !('id' in bot)) {
    console.warn(`No bot found for ID ${botId}`);
    return null;
  }

const sanitizedBot = {
    id: bot.id,
    created: String(bot.created), // Ensure string
    name: bot.name || "", // Fallback for title
    type: bot.type || "", // Fallback for text
    user : {
     id: bot.user?.id || "",
     username: bot.user?.username || "" 
    }
}

// Transform into a sanitized shape
return sanitizedBot
}
