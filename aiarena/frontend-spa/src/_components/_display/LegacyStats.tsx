import { graphql, useLazyLoadQuery } from "react-relay";
import WrappedTitle from "./WrappedTitle";
import { LegacyStatsQuery } from "./__generated__/LegacyStatsQuery.graphql";
import FetchError from "./FetchError";

const LegacyStats: React.FC = () => {
  const data = useLazyLoadQuery<LegacyStatsQuery>(
    graphql`
      query LegacyStatsQuery {
        stats {
          arenaclients
          buildNumber
          dateTime
          matchCount1h
          matchCount24h
          matchesQueued
          matchesStarted
        }
      }
    `,
    {}
  );

  if (!data.stats) {
    return <FetchError type="stats" />;
  }

  const formattedDateTime = data.stats.dateTime
    ? new Date(data.stats.dateTime).toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "-";

  const rows: { label: string; value: React.ReactNode; link?: string }[] = [
    { label: "Build", value: data.stats.buildNumber ?? "-" },
    {
      label: "Arena Clients",
      value: data.stats.arenaclients ?? 0,
      link: "/arenaclients/",
    },
    {
      label: "Match Queue",
      value: data.stats.matchesQueued,
      link: "/match-queue/",
    },
    { label: "Matches Playing", value: data.stats.matchesStarted },
    { label: "Matches last hour", value: data.stats.matchCount1h ?? 0 },
    { label: "Matches last 24h", value: data.stats.matchCount24h ?? 0 },
    { label: "Server Time", value: formattedDateTime },
  ];

  return (
    <div className="mb-8">
      <WrappedTitle title="Stats" font="font-bold" />

      <table className="w-full mt-2">
        <thead className="bg-customGreen-dark-2 h-9">
          <tr>
            <th className="text-left pl-3">Metric</th>
            <th className="text-right pr-3">Value</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr
              key={row.label}
              className={`text-sm h-10 ${
                idx % 2 ? "bg-darken-4" : "bg-darken"
              }`}
            >
              <td className="pl-3 font-semibold">
                {row.link ? (
                  <a
                    title={`${row.label}`}
                    aria-label={`Navigate to ${row.label}`}
                    href={`${row.link}`}
                  >
                    {row.label}
                  </a>
                ) : (
                  row.label
                )}
              </td>
              <td className="pr-3 text-right">{row.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LegacyStats;
