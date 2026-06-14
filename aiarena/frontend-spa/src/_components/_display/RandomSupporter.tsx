import { graphql, useLazyLoadQuery } from "react-relay";
import { RandomSupporterQuery } from "./__generated__/RandomSupporterQuery.graphql";
import { getIDFromBase64 } from "@/_lib/relayHelpers";
import { reverseUrl } from "@/_lib/reverseUrl";
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

  const supporter = data.stats?.randomSupporter;
  if (!supporter) {
    return null;
  }

  return (
    <Link
      className="mb-6 text-2xl font-bold"
      to={reverseUrl("author", {
        pk: getIDFromBase64(supporter.id, "UserType"),
      })}
    >
      {supporter.username}
    </Link>
  );
}
