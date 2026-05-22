import { graphql, useLazyLoadQuery } from "react-relay";

import { DevelopersQuery } from "./__generated__/DevelopersQuery.graphql";
import DevelopersContent from "./DevelopersContent";

export default function Developers() {
  const data = useLazyLoadQuery<DevelopersQuery>(
    graphql`
      query DevelopersQuery {
        viewer {
          apiToken
          user {
            username
          }
        }
        rounds(last: 1) {
          edges {
            node {
              id
            }
          }
        }
      }
    `,
    {},
  );

  const sampleRoundId = data.rounds?.edges?.[0]?.node?.id ?? null;

  return (
    <DevelopersContent
      apiToken={data.viewer?.apiToken ?? null}
      isLoggedIn={Boolean(data.viewer?.user)}
      sampleRoundId={sampleRoundId}
    />
  );
}
