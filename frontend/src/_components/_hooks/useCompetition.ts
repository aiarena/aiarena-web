// Import necessary modules and types
import { useLazyLoadQuery, graphql } from 'react-relay';
import { getNodes } from "@/_lib/relayHelpers"; // Ensure this path is correct
import { useCompetitionQuery } from './__generated__/useCompetitionQuery.graphql';

// Define the hook with TypeScript generics
export const useCompetition = (competitionId: string) => {
  // Execute the GraphQL query with the competitionId variable
  const data = useLazyLoadQuery<useCompetitionQuery>(
    graphql`
      query useCompetitionQuery($id: ID!) {
        competitions(id: $id) {
          edges {
            node {
              id
              participants {
                edges {
                  node {
                    id
                    elo
                    bot {
                      id
                      name
                      type
                      user {
                        email
                        id
                        patreonLevel
                      }
                    }
                    trend
                    divisionNum
                  }
                }
                pageInfo {
                  startCursor
                  endCursor
                }
              }
              dateClosed
              dateCreated
              dateOpened
              name
              status
            }
          }
          pageInfo {
            startCursor
            endCursor
            hasNextPage
          }
          totalCount
        }
      }
    `,
    { id: competitionId }
  );

  // Extract competition nodes using the helper function
  const competitionNodes = getNodes(data.competitions);

  // Ensure that exactly one competition is fetched
  if (competitionNodes.length !== 1) {
    console.warn(`Expected exactly one competition for ID ${competitionId}, but got ${competitionNodes.length}`);
  }

  const competition = competitionNodes[0];

  // Sanitize and transform the competition data
  const sanitizedCompetition = {
    id: competition?.id || '',
    name: competition?.name || '',
    status: competition?.status || '',
    dateCreated: competition?.dateCreated ? String(competition.dateCreated) : '',
    dateOpened: competition?.dateOpened ? String(competition.dateOpened) : '',
    dateClosed: competition?.dateClosed ? String(competition.dateClosed) : '',
    participants: competition?.participants
      ? getNodes(competition.participants).map((participant) => ({
          id: participant.id,
          elo: participant.elo,
          trend: participant.trend,
          divisionNum: participant.divisionNum,
          bot: participant.bot
            ? {
                id: participant.bot.id,
                name: participant.bot.name || '',
                type: participant.bot.type || '',
                user: participant.bot.user
                  ? {
                      id: participant.bot.user.id,
                      email: participant.bot.user.email || '',
                      patreonLevel: participant.bot.user.patreonLevel || 0,
                    }
                  : null,
              }
            : null,
        }))
      : [],
  };

  console.log("Sanitized Competition data:", sanitizedCompetition);

  return sanitizedCompetition;
};
