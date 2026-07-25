import { graphql, useLazyLoadQuery } from "react-relay";

import AdminStatsChart from "./AdminStatsChart";
import { AdminStatsQuery } from "./__generated__/AdminStatsQuery.graphql";

export default function AdminStats() {
  const data = useLazyLoadQuery<AdminStatsQuery>(
    graphql`
      query AdminStatsQuery {
        statsForAdmins {
          ...AdminStatsChart_node
        }
      }
    `,
    {},
    {
      fetchPolicy: "network-only",
    },
  );

  if (!data.statsForAdmins) {
    return (
      <div className="rounded-xl border border-neutral-800 bg-darken-2 p-6 shadow-lg backdrop-blur-lg">
        <p className="text-center text-neutral-300">
          You do not have permission to view admin statistics.
        </p>
      </div>
    );
  }

  return <AdminStatsChart data={data.statsForAdmins} />;
}
