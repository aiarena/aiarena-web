import { graphql, useLazyLoadQuery } from "react-relay";
import { useUserQuery } from "./__generated__/useUserQuery.graphql";

export const useUser = (userId: string) => {
  const data = useLazyLoadQuery<useUserQuery>(
    graphql`
      query useUserQuery($id: ID!) {
        node(id: $id) {
          ... on UserType {
            id
            username
            patreonLevel
            dateJoined
            avatarUrl
            bots {
              edges {
                node {
                  id
                  name

                  type
                  playsRace
                }
              }
            }
          }
        }
      }
    `,
    { id: userId },
  );

  const user = data.node;
  if (!user || !("id" in user)) {
    console.warn(`No user found for ID ${userId}`);
    return null;
  }

  // Transform into a sanitized shape
  return {
    id: user.id,
    dateJoined: String(user.dateJoined), // Ensure string
    username: user.username || "", // Fallback for title
    patreonLevel: user.patreonLevel || "", // Fallback for text
    avatarUrl: user.avatarUrl || "",
    bots:
      data.node?.bots?.edges?.map((edge) => ({
        name: edge?.node?.name || "",
        type: edge?.node?.type || "",
        id: edge?.node?.id || "",
        playsRace: edge?.node?.playsRace || "",
      })) || [],
  };
};
