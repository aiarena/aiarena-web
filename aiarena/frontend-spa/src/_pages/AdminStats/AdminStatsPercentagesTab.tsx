import { useMemo } from "react";
import { graphql, useFragment, useLazyLoadQuery } from "react-relay";

import AdminStatsChartSection from "./AdminStatsChartSection";
import { AdminStatsMessage, AdminStatsTabSuspense } from "./AdminStatsMessage";
import {
  clipToPeriod,
  createDailyDateRange,
  formatPercent,
  getPeriodStart,
  lineDataset,
  numberFormat,
  sumInPeriod,
  toDailyCounts,
  toPercentageSeries,
} from "./adminStatsSeries";
import useAdminStatsParams from "./useAdminStatsParams";
import { AdminStatsPercentagesTabQuery } from "./__generated__/AdminStatsPercentagesTabQuery.graphql";
import { AdminStatsPercentagesTab_stats$key } from "./__generated__/AdminStatsPercentagesTab_stats.graphql";

function AdminStatsPercentagesTabContent() {
  const data = useLazyLoadQuery<AdminStatsPercentagesTabQuery>(
    graphql`
      query AdminStatsPercentagesTabQuery {
        statsForAdmins {
          ...AdminStatsPercentagesTab_stats
        }
      }
    `,
    {},
    { fetchPolicy: "store-and-network" },
  );

  const stats = useFragment<AdminStatsPercentagesTab_stats$key>(
    graphql`
      fragment AdminStatsPercentagesTab_stats on StatsForAdmins {
        newUsers {
          dateTime
          count
        }
        newUsersWithAtLeastOneBot {
          dateTime
          count
        }
        newPatreonUsers {
          dateTime
          count
        }
      }
    `,
    data.statsForAdmins,
  );

  const { period, periodConfig } = useAdminStatsParams();

  const series = useMemo(() => {
    if (!stats) return null;

    const usersDaily = toDailyCounts(stats.newUsers);
    const raw = [
      {
        label: "Users with a bot",
        color: "#38bdf8",
        daily: toDailyCounts(stats.newUsersWithAtLeastOneBot),
      },
      {
        label: "Patreon donators",
        color: "#f472b6",
        daily: toDailyCounts(stats.newPatreonUsers),
      },
    ];

    const dates = createDailyDateRange([usersDaily, ...raw.map((s) => s.daily)]);

    return {
      usersDaily,
      lines: raw.map((s) => ({
        ...s,
        cumulative: toPercentageSeries(dates, s.daily, usersDaily),
      })),
    };
  }, [stats]);

  if (!stats) {
    return (
      <AdminStatsMessage>
        You do not have permission to view admin statistics.
      </AdminStatsMessage>
    );
  }

  if (!series || !series.lines[0].cumulative.length) {
    return <AdminStatsMessage>No admin statistics are available.</AdminStatsMessage>;
  }

  const periodStart = getPeriodStart(period);
  const isAllTime = periodStart === null;
  const usersInPeriod = sumInPeriod(series.usersDaily, periodStart);

  return (
    <AdminStatsChartSection
      cards={series.lines.map((s) => {
        const inPeriod = sumInPeriod(s.daily, periodStart);

        return {
          label: isAllTime ? s.label : `${s.label} (new users)`,
          value: formatPercent(inPeriod, usersInPeriod),
          detail: `${numberFormat.format(inPeriod)} of ${numberFormat.format(usersInPeriod)} users`,
          color: s.color,
        };
      })}
      data={{
        datasets: series.lines.map((s) =>
          lineDataset(s.label, s.color, clipToPeriod(s.cumulative, periodStart)),
        ),
      }}
      timeUnit={periodConfig.timeUnit}
      yTitle="Percentage of total users"
      gridColor="rgba(134,194,50,0.12)"
      yMax={100}
      formatTick={(value) => `${value}%`}
      formatTooltipLabel={(item) =>
        `${item.dataset.label}: ${(item.parsed.y ?? 0).toFixed(2)}%`
      }
    />
  );
}

export default function AdminStatsPercentagesTab() {
  return (
    <AdminStatsTabSuspense>
      <AdminStatsPercentagesTabContent />
    </AdminStatsTabSuspense>
  );
}
