import { graphql, useFragment } from "react-relay";

import { AuthorMatchRequests_user$key } from "./__generated__/AuthorMatchRequests_user.graphql";
import AuthorMatchRequestsTable from "./AuthorMatchRequestsTable";

interface AuthorMatchRequestsProps {
  data: AuthorMatchRequests_user$key;
}

export default function AuthorMatchRequests(props: AuthorMatchRequestsProps) {
  const data = useFragment(
    graphql`
      fragment AuthorMatchRequests_user on UserType
      @argumentDefinitions(
        orderBy: { type: "String" }
        showEveryonesTags: { type: "Boolean", defaultValue: false }
      ) {
        ...AuthorMatchRequestsTable_user
          @arguments(orderBy: $orderBy, showEveryonesTags: $showEveryonesTags)
      }
    `,
    props.data,
  );

  return (
    <section className="h-full" aria-labelledby="author-match-requests-heading">
      <h2 id="author-match-requests-heading" className="sr-only">
        Author Match Requests
      </h2>

      <AuthorMatchRequestsTable data={data} />
    </section>
  );
}
