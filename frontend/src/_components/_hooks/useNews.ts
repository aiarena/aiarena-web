import { useLazyLoadQuery, graphql } from 'react-relay';
import {nodes} from "@/_lib/relayHelpers";

export const useNews = () => {
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
  );
  return nodes(data.news);
};
