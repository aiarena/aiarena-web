import { useLazyLoadQuery, graphql } from 'react-relay';
import { nodes } from "@/_lib/relayHelpers";
import { AssertionError } from 'assert';

type NewsItem = {
  id: string;
  title: string;
  text: string;
  created: string;
  ytLink?: string; // Exclude null
};

// USES TYPE ASSERTION; ADD DYNAMIC TYPES WITH RELAY

export const useNews = (): NewsItem[] => {
  const data = useLazyLoadQuery(
    graphql`
      query useNewsQuery {
        news(last: 5) {
          edges {
            node {
              id
              title
              text
              created
              ytLink
            }
          }
        }
      }
    `,
    {},
  ) as {
    news: {
      edges: {
        node: {
          id: string;
          title: string;
          text: string;
          created: string;
          ytLink?: string | null;
        };
      }[];
    };
  }; // Assert the type

  // Transform to exclude null ytLink values
  return nodes(data.news).map((item) => ({
    ...item,
    ytLink: item.ytLink ?? undefined,
  }));
};
