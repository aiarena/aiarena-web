import { graphql, useFragment } from "react-relay";
import { Suspense, useState } from "react";
import { UserMatchRequestsSection_viewer$key } from "./__generated__/UserMatchRequestsSection_viewer.graphql";
import MatchRequestsTable from "../_props/MatchRequestsTable";
import LoadingSpinner from "../_display/LoadingSpinnerGray";
import UserMatchRequestsHeaderSection from "./UserMatchRequestsHeaderSection";
import SuspenseGetLoading from "../_props/SuspenseGetLoading";

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
        ...MatchRequestsTable_viewer @arguments(orderBy: $orderBy)
      }
    `,
    props.viewer
  );
  const [matchRequestsLoading, setMatchRequestsLoading] = useState(false);

  return (
    <section className="h-full" aria-labelledby="match-requests-heading">
      <h2 id="match-requests-heading" className="sr-only">
        Match Requests
      </h2>
      <Suspense fallback={<LoadingSpinner />}>
        <UserMatchRequestsHeaderSection viewer={viewer} />
      </Suspense>
      <div role="region" aria-labelledby="match-requests-table-heading">
        <h3 id="match-requests-table-heading" className="sr-only">
          Match Requests Table
        </h3>
        <Suspense
          fallback={<SuspenseGetLoading setLoading={setMatchRequestsLoading} />}
        >
          <MatchRequestsTable viewer={viewer} loading={matchRequestsLoading} />
        </Suspense>
        {matchRequestsLoading ? (
          <MatchRequestsTable viewer={viewer} loading={matchRequestsLoading} />
        ) : null}
      </div>
    </section>
  );
}
