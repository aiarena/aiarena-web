import { graphql, useLazyLoadQuery } from "react-relay";
import { useParams } from "react-router";

import { getBase64FromID } from "@/_lib/relayHelpers";
import FetchError from "@/_components/_display/FetchError";
import { ArenaClientSectionQuery } from "./__generated__/ArenaClientSectionQuery.graphql";
import ArenaClientHeader from "./ArenaClientHeader";
import AssignedMatches from "./AssignedMatches";
import ArenaClientResults from "./ArenaClientResults";

export default function ArenaClientSection() {
  const { arenaClientId } = useParams<{ arenaClientId: string }>();

  const data = useLazyLoadQuery<ArenaClientSectionQuery>(
    graphql`
      query ArenaClientSectionQuery($id: ID!) {
        node(id: $id) {
          ... on ArenaClientType {
            ...ArenaClientHeader_arenaClient
            ...AssignedMatches_arenaClient
            ...ArenaClientResults_arenaClient
          }
        }
      }
    `,
    { id: getBase64FromID(arenaClientId!, "ArenaClientType") || "" },
  );

  if (!data.node) {
    return <FetchError type="arena client" />;
  }

  return (
    <>
      <div className="mb-8">
        <ArenaClientHeader arenaClient={data.node} />
      </div>

      <section className="mb-8" aria-labelledby="assigned-matches-heading">
        <h4 id="assigned-matches-heading" className="mb-4">
          Assigned Matches
        </h4>
        <AssignedMatches arenaClient={data.node} />
      </section>

      <section className="mb-8" aria-labelledby="recent-results-heading">
        <h4 id="recent-results-heading" className="mb-4">
          Recent Results
        </h4>
        <ArenaClientResults arenaClient={data.node} />
      </section>
    </>
  );
}
