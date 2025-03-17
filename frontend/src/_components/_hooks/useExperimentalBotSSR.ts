"use server";
import { cookies } from 'next/headers';

export interface BotSSRData {
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
}

// Fetch basic bot information on server
export async function getBotBasic(botId: string): Promise<BotSSRData | null> {
  try {
    const csrftoken = cookies().get("csrftoken")?.value;
    const sessionid = cookies().get("sessionid")?.value;
    
    const response = await fetch(`${process.env.API_URL}/graphql/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Cookie": `csrftoken=${csrftoken}; sessionid=${sessionid}`
      },
      body: JSON.stringify({
        query: `
          query BotBasicQuery($id: ID!) {
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
              }
            }
          }
        `,
        variables: { id: botId },
      }),
      cache: 'no-store' // Disable caching to ensure fresh data
    });
    
    const result = await response.json();
    const bot = result.data?.node;
    
    if (!bot || !('id' in bot)) {
      console.error("Failed to fetch bot data or invalid data structure:", result);
      return null;
    }
    
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
      }
    };
  } catch (error) {
    console.error("Error fetching bot basic info:", error);
    return null;
  }
}