import { graphql, useLazyLoadQuery } from "react-relay";
import { GetGameOfInterestQuery } from "./__generated__/GetGameOfInterestQuery.graphql";
import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";

export default function GetGameOfInterest() {
  const data = useLazyLoadQuery<GetGameOfInterestQuery>(
    graphql`
      query GetGameOfInterestQuery {
        viewer {
          requestedMatches(first: 50) {
            edges {
              node {
                id
                result {
                  winner {
                    name
                  }
                }
              }
            }
          }
        }
      }
    `,
    {}
  );

  const possibleMatches = getNodes(data.viewer?.requestedMatches).filter(
    (item) => {
      return item.result?.winner?.name ? item.id : false;
    }
  );

  const matchSuggestion =
    possibleMatches &&
    possibleMatches[0]?.id &&
    getIDFromBase64(possibleMatches[0].id, "MatchType");

  return <>{`!queue ${matchSuggestion ? matchSuggestion : "match_id"}`}</>;
}
