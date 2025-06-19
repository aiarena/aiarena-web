import { graphql, useFragment } from "react-relay";
import { UserMatchRequestsSection_viewer$key } from "./__generated__/UserMatchRequestsSection_viewer.graphql";
import UserMatchRequestsTable from "./UserMatchRequests/UserMatchRequestsTable";
import UserMatchRequestsHeaderSection from "./UserMatchRequests/UserMatchRequestsHeaderSection";

interface UserMatchRequestsSectionProps {
  viewer: UserMatchRequestsSection_viewer$key;
}

export default function UserMatchRequestsSection(
  props: UserMatchRequestsSectionProps
) {
  const viewer = useFragment(
    graphql`
      fragment UserMatchRequestsSection_viewer on Viewer
      @argumentDefinitions(orderBy: { type: "String" }) {
        ...UserMatchRequestsHeaderSection_viewer
        ...UserMatchRequestsTable_viewer @arguments(orderBy: $orderBy)
      }
    `,
    props.viewer
  );

  return (
    <section className="h-full" aria-labelledby="match-requests-heading">
      <h2 id="match-requests-heading" className="sr-only">
        Match Requests
      </h2>

      <UserMatchRequestsHeaderSection viewer={viewer} />

      <div role="region" aria-labelledby="match-requests-table-heading">
        <h3 id="match-requests-table-heading" className="sr-only">
          Match Requests Table
        </h3>

        <UserMatchRequestsTable viewer={viewer} />
      </div>
    </section>
  );
}
