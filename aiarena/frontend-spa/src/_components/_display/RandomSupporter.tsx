import { graphql, useLazyLoadQuery } from "react-relay";
import { RandomSupporterQuery } from "./__generated__/RandomSupporterQuery.graphql";
import { getIDFromBase64 } from "@/_lib/relayHelpers";

export default function RandomSupporter() {
  const data = useLazyLoadQuery<RandomSupporterQuery>(
    graphql`
      query RandomSupporterQuery {
        stats {
          randomSupporter {
            username
            id
          }
        }
      }
    `,
    {}
  );

  return (
    <a
      className="mb-6 text-2xl font-bold"
      href={`/authors/${getIDFromBase64(data.stats?.randomSupporter?.id, "UserType")}`}
    >
      {data.stats?.randomSupporter?.username}
    </a>
  );
}
