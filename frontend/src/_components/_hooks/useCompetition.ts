import { useLazyLoadQuery, graphql } from "react-relay";
import { useCompetitionQuery } from "./__generated__/useCompetitionQuery.graphql";

export const useCompetition = (competitionId: string) => {
  // Execute the query to fetch competition data
  const data = useLazyLoadQuery<useCompetitionQuery>(
    graphql`
      query useCompetitionQuery($id: ID!) {
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
            maps {
              edges {
                node {
                  id
                  name
                  downloadLink
                }
              }
            }
            dateClosed
            dateCreated
            dateOpened
            name
            status
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
    name: competition.name || "",
    status: competition.status || "",
    dateCreated: competition.dateCreated || "",
    dateOpened: competition.dateOpened || "",
    dateClosed: competition.dateClosed || "",
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
    maps:
      competition.maps?.edges
        ?.map((edge) => edge?.node)
        .filter((map): map is NonNullable<typeof map> => !!map)
        .map((map) => ({
          id: map.id,
          name: map.name || "",
          downloadLink: map.downloadLink || "",
        })) || [], // Default to an empty array if undefined
  };

  return sanitizedCompetition;
};
