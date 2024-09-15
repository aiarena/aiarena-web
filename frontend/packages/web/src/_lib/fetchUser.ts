import { graphql } from 'react-relay';
import { fetchQuery } from 'relay-runtime';
import environment from '@/_lib/RelayEnvironment'; // Relay environment setup

// Fetch the current user's data
export const fetchUser = async () => {
  const query = graphql`
    query fetchUserQuery {
      viewer {
        id
        username
        email
        patreonLevel
        dateJoined
      }
    }
  `;

  try {
    const data = await fetchQuery(environment, query, {}).toPromise(); // Ensure the network request resolves
    if (data && data.viewer) {
      return data.viewer; // Return the fetched user data
    } else {
      console.warn('No viewer data available');
      return null;
    }
  } catch (error) {
    console.error('Failed to fetch user data:', error);
    return null; // Handle errors and return null
  }
};
