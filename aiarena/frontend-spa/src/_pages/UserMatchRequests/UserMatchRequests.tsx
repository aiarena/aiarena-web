import { graphql, useLazyLoadQuery } from "react-relay";
import RequestMatchSection from "@/_components/_sections/UserMatchRequestsSection";
import { UserMatchRequestsQuery } from "./__generated__/UserMatchRequestsQuery.graphql";

export default function UserMatchRequests() {
  const data = useLazyLoadQuery<UserMatchRequestsQuery>(
    graphql`
      query UserMatchRequestsQuery {
        viewer {
          ...UserMatchRequestsSection_viewer
        }
      }
    `,
    {}
  );

  if (!data.viewer) {
    window.location.replace("/accounts/login");
    return null;
  }

  return (
    <>
      <RequestMatchSection viewer={data.viewer} />
    </>
  );
}
