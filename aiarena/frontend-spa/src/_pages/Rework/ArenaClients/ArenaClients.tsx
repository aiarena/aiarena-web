import { graphql, useLazyLoadQuery } from "react-relay";

import { ArenaClientsQuery } from "./__generated__/ArenaClientsQuery.graphql";
import ArenaClientsTable from "./ArenaClientsTable";
import FetchError from "@/_components/_display/FetchError";

export default function ArenaClients() {
  const data = useLazyLoadQuery<ArenaClientsQuery>(
    graphql`
      query ArenaClientsQuery {
        ...ArenaClientsTable_node
      }
    `,
    {},
  );

  if (!data) {
    return <FetchError type="arena clients" />;
  }

  return (
    <section aria-labelledby="arena-clients-heading">
      <h2 id="arena-clients-heading" className="sr-only">
        Arena Clients
      </h2>
      <ArenaClientsTable data={data} />
    </section>
  );
}
