"use client";

import { useLazyLoadQuery, graphql } from 'react-relay';
import { useExperimentalBotClientRenderQuery } from './__generated__/useExperimentalBotClientRenderQuery.graphql';

export interface BotParticipationsData {
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

export const useBotParticipations = (botId: string): BotParticipationsData | null => {
  const data = useLazyLoadQuery<useExperimentalBotClientRenderQuery>(
    graphql`
      query useExperimentalBotClientRenderQuery($id: ID!) {
        node(id: $id) {
          ... on BotType {
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
  if (!bot) {
    return null;
  }
  
  return {
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