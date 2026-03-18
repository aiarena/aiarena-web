import { graphql, useLazyLoadQuery } from "react-relay";
import { RandomSupporterQuery } from "./__generated__/RandomSupporterQuery.graphql";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { Link } from "react-router";

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
    {},
  );

  return (
    <Link
      className="mb-6 text-2xl font-bold"
      to={`/authors/${getIDFromBase64(data.stats?.randomSupporter?.id, "UserType")}`}
    >
      {data.stats?.randomSupporter?.username}
    </Link>
  );
}
