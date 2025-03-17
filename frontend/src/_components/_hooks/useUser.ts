import { useLazyLoadQuery, graphql } from 'react-relay';
import { getNodes, nodes } from "@/_lib/relayHelpers";

import { getDataIDsFromFragment } from 'relay-runtime';
import { useUserQuery } from './__generated__/useUserQuery.graphql';

export const useUser = (userId: string) => {
    console.log("attempting to get user with," , userId)
  const data = useLazyLoadQuery<useUserQuery>(
    graphql`
      query useUserQuery($id: ID!) {
        node(id: $id) {
          ...on UserType{
              id    
              username
              patreonLevel
              dateJoined
          }
        }
      }
    `,
    { id: userId }
  );    




const user = data.node;
if (!user || !('id' in user)) {
    console.warn(`No user found for ID ${userId}`);
    return null;
  }

const sanitizedBot = {
    id: user.id,
    dateJoined: String(user.dateJoined), // Ensure string
    username: user.username || "", // Fallback for title
    patreonLevel: user.patreonLevel || "", // Fallback for text
   
}

// Transform into a sanitized shape
return sanitizedBot
}
