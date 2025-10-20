import { graphql, useLazyLoadQuery } from "react-relay";

import { UserMatchRequestsQuery } from "./__generated__/UserMatchRequestsQuery.graphql";
import UserMatchRequestsSection from "@/_pages/UserMatchRequests/UserMatchRequestsSection";

export default function UserMatchRequests() {
  const data = useLazyLoadQuery<UserMatchRequestsQuery>(
    graphql`
      query UserMatchRequestsQuery($orderBy: String) {
        viewer {
          ...UserMatchRequestsSection_viewer @arguments(orderBy: $orderBy)
        }
      }
    `,
    {
      orderBy: "",
    },
  );

  if (!data.viewer) {
    window.location.replace("/accounts/login");
    return null;
  }

  return (
    <>
      <UserMatchRequestsSection viewer={data.viewer} />
    </>
  );
}
