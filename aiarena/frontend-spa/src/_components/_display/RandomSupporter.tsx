import { graphql, useLazyLoadQuery } from "react-relay";
import { RandomSupporterQuery } from "./__generated__/RandomSupporterQuery.graphql";

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
    <p className="mb-6 text-xl font-bold">
      {data.stats?.randomSupporter?.username}
    </p>
  );
}
