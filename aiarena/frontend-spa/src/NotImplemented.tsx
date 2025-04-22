import { graphql, useLazyLoadQuery } from "react-relay";
import { NotImplementedQuery } from "./__generated__/NotImplementedQuery.graphql";

export default function NotImplemented() {
  const { viewer } = useLazyLoadQuery<NotImplementedQuery>(
    graphql`
      query NotImplementedQuery {
        viewer {
          email
        }
      }
    `,
    {}
  );

  if (!viewer) {
    return <span>Not logged in</span>;
  }

  return <span>Logged in as {viewer.email}</span>;
}
