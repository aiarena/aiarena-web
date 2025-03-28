import { useLazyLoadQuery, graphql } from "react-relay";
import { useCompetitionDataQuery } from "./__generated__/useCompetitionDataQuery.graphql";

export const useCompetitionData = (competitionId: string) => {
  // Execute the query to fetch competition data
  const data = useLazyLoadQuery<useCompetitionDataQuery>(
    graphql`
      query useCompetitionDataQuery($id: ID!) {
        node(id: $id) {
          ... on CompetitionType {
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
                      id
                      patreonLevel
                      username
                    }
                  }
                  trend
                  divisionNum
                }
              }
            }
            rounds {
              edges {
                node {
                  id
                  finished
                  started
                  number
                  complete
                }
              }
            }
          }
        }
      }
    `,
    { id: competitionId },
  );

  // Handle the case where no data is returned
  const competition = data.node;
  if (!competition || !("id" in competition)) {
    console.warn(`No competition found for ID ${competitionId}`);
    return null;
  }

  // Sanitize and transform the competition data
  const sanitizedCompetition = {
    id: competition.id,
    participants:
      competition.participants?.edges
        ?.map((edge) => edge?.node)
        .filter(
          (participant): participant is NonNullable<typeof participant> =>
            !!participant,
        )
        .map((participant) => ({
          id: participant.id,
          elo: participant.elo,
          trend: participant.trend,
          divisionNum: participant.divisionNum,
          bot: participant.bot
            ? {
              id: participant.bot.id,
              name: participant.bot.name || "",
              type: participant.bot.type || "",
              user: participant.bot.user
                ? {
                  id: participant.bot.user.id,
                  patreonLevel: participant.bot.user.patreonLevel || "NONE",
                  username: participant.bot.user.username || "",
                }
                : null,
            }
            : null,
        })) || [], // Default to an empty array if undefined
    rounds:
      competition.rounds?.edges
        ?.map((edge) => edge?.node)
        .filter((round): round is NonNullable<typeof round> => !!round)
        .map((round) => ({
          id: round.id,
          finished: round.finished || false,
          started: round.started || "",
          number: round.number || 0,
          complete: round.complete || false,
        })) || [], // Default to an empty array if undefined
  };

  return sanitizedCompetition;
};
