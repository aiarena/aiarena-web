import { useLazyLoadQuery, graphql } from 'react-relay';
import { getNodes } from "@/_lib/relayHelpers";
import { useUserBotsQuery } from './__generated__/useUserBotsQuery.graphql';

export const useUserBots = (userId: string | null) => {
  // Always call the query hook, but provide a fallback userId if it's null
  const data = useLazyLoadQuery<useUserBotsQuery>(
    graphql`
      query useUserBotsQuery($userId: ID!) {
        bots(userId: $userId) {
          edges {
            node {
              id    
              name
              created
              type
              url
              botData
              botDataEnabled
              botDataPubliclyDownloadable
              botZip
              botZipPubliclyDownloadable
              botZipUpdated
              wikiArticle
              competitionParticipations {
                edges {
                  node {
                    active
                    id
                    competition {
                      name
                      status
                    }
                    elo
                    divisionNum
                    crashPerc
                    crashCount
                    trend
                    matchCount
                    winPerc
                    lossPerc
                  }
                }
              }
            }
          }
        }
      }
    `,

    { userId: userId || "default" } // Provide a default placeholder
  );

  // Handle cases where no userId is passed
  if (!userId) {
    console.log("No userId.")
    return [];
  }

  // Extract nodes and transform them into the required shape
  const botNodes = getNodes(data.bots);
  return botNodes.map((node) => ({
    id: node.id,
    name: node.name || "", // Fallback for title
    created: String(node.created), // Ensure string
    type: node.type || "", // Fallback for type
    url: node.url || "",
    wikiArticle: node?.wikiArticle || "",
    botData: node.botData || "",
    botDataEnabled: node.botDataEnabled || false,
    botDataPubliclyDownloadable: node.botDataPubliclyDownloadable || false,
    botZip: node.botZip || "",
    botZipPubliclyDownloadable: node.botZipPubliclyDownloadable || false,
    botZipUpdated: node.botZipUpdated || undefined,
    competitionParticipations: getNodes(node.competitionParticipations).map((participation) => ({
      active: participation.active || false,
      id: participation.id,
      competition: {
        name: participation.competition?.name || "",
        status: participation.competition?.status || "",
      },
      elo: participation.elo || 0,
      divisionNum: participation.divisionNum || 0,
      crashPerc: participation.crashPerc || 0,
      crashCount: participation.crashCount || 0,
      trend: participation.trend || 0,
      matchCount: participation.matchCount || 0,
      winPerc: participation.winPerc || 0,
      lossPerc: participation.lossPerc || 0,
    })),
  }));
};
