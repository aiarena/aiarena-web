  import { useLazyLoadQuery, graphql } from 'react-relay';
  import { useBotQuery } from './__generated__/useBotQuery.graphql';

  export interface Bot {
    id: string;
    name: string;
    type: string;
    created: string;
    botZipUpdated: string;
    wikiArticle: string;
    user: {
      id: string;
      username: string;
    };
    matchParticipations: {
      avgStepTime: number;
      eloChange: number;
      result: string;
      match: { id: string; status: string; started: string };
    }[];
    competitionParticipations: {
      competition: { name: string; status: string };
      divisionNum: number;
      elo: number;
    }[];
  }

  export const useBot = (botId: string): Bot | null => {
    console.log("Attempting to get bot with:", botId);

    const data = useLazyLoadQuery<useBotQuery>(
      graphql`
        query useBotQuery($id: ID!) {
          node(id: $id) {
            ... on BotType {
              id
              name
              type
              created
              botZipUpdated
              wikiArticle
              user {
                id
                username
              }
              competitionParticipations {
                edges {
                  node {
                    competition {
                      status
                      name
                    }
                    divisionNum
                    elo
                  }
                }
              }
              matchParticipations {
                edges {
                  node {
                    avgStepTime
                    eloChange
                    result
                    match {
                      id
                      started
                      status
                    }
                  }
                }
              }
            }
          }
        }
      `,
      { id: botId }
    );

    const bot = data.node;
    if (!bot || !('id' in bot)) {
      return null;
    }

    // Sanitized data shape
    return {
      id: bot.id ?? "",
      name: bot.name || "",
      type: bot.type || "",
      created: bot.created || "",
      botZipUpdated: bot.botZipUpdated || "",
      wikiArticle: bot.wikiArticle || "",
      user: {
        id: bot.user?.id || "",
        username: bot.user?.username || "",
      },
      matchParticipations:
        bot.matchParticipations?.edges?.map((edge) => ({
          avgStepTime: edge?.node?.avgStepTime || 0,
          eloChange: edge?.node?.eloChange || 0,
          result: edge?.node?.result || "",
          match: {
            id: edge?.node?.match?.id || "",
            started: edge?.node?.match?.started || "",
            status: edge?.node?.match?.status || "",
          },
        })) || [],
      competitionParticipations:
        bot.competitionParticipations?.edges?.map(edge => ({
          competition: {
            status: edge?.node?.competition?.status || "",
            name: edge?.node?.competition?.name || "",
          },
          divisionNum: edge?.node?.divisionNum || 0,
          elo: edge?.node?.elo || 0,
        })) || [],
    };
  };
