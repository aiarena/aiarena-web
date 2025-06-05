import { graphql } from "react-relay";
import { fetchQuery } from "relay-runtime";
import environment from "@/_lib/RelayEnvironment"; // Relay environment setup
import { fetchViewerQuery } from "./__generated__/fetchViewerQuery.graphql";
import { Viewer } from "@/_components/_hooks/useViewer";

// Fetch the current user's data
export const fetchViewer = async () => {
  const query = graphql`
    query fetchViewerQuery {
      viewer {
        apiToken
        email
        activeBotParticipations
        activeBotParticipationLimit
        requestMatchesLimit
        requestMatchesCountLeft
        user {
          id
          username
          patreonLevel
          dateJoined
          avatarUrl
        }
      }
    }
  `;

  try {
    const data = await fetchQuery<fetchViewerQuery>(
      environment,
      query,
      {},
    ).toPromise(); // Ensure the network request resolves
    if (data && data.viewer) {
      return data.viewer as Viewer; // Return the fetched user data
    } else {
      console.warn("No viewer data available");
      return null;
    }
  } catch (error) {
    console.error("Failed to fetch user data:", error);
    return null; // Handle errors and return null
  }
};
