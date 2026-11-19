import { useMemo } from "react";
import { graphql, useFragment, useLazyLoadQuery } from "react-relay";

import AdminStatsChartSection from "./AdminStatsChartSection";
import { AdminStatsMessage, AdminStatsTabSuspense } from "./AdminStatsMessage";
import {
  barDataset,
  createBuckets,
  DAY_IN_MS,
  getPeriodStart,
  getTodayUtcTimestamp,
  numberFormat,
  sumInPeriod,
  toBucketedSeries,
  toDailyCounts,
} from "./adminStatsSeries";
import useAdminStatsParams from "./useAdminStatsParams";
import { AdminStatsActivityTabQuery } from "./__generated__/AdminStatsActivityTabQuery.graphql";
import { AdminStatsActivityTab_stats$key } from "./__generated__/AdminStatsActivityTab_stats.graphql";

function AdminStatsActivityTabContent() {
  const data = useLazyLoadQuery<AdminStatsActivityTabQuery>(
    graphql`
      query AdminStatsActivityTabQuery {
        statsForAdmins {
          ...AdminStatsActivityTab_stats
        }
      }
    `,
    {},
    { fetchPolicy: "store-and-network" },
  );

  const stats = useFragment<AdminStatsActivityTab_stats$key>(
    graphql`
      fragment AdminStatsActivityTab_stats on StatsForAdmins {
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
        newBots {
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

    return [
      {
        label: "New users",
        color: "#86c232",
        daily: toDailyCounts(stats.newUsers),
      },
      {
        label: "New users with a bot",
        color: "#38bdf8",
        daily: toDailyCounts(stats.newUsersWithAtLeastOneBot),
      },
      {
        label: "New Patreon donators",
        color: "#f472b6",
        daily: toDailyCounts(stats.newPatreonUsers),
      },
      {
        label: "New bots",
        color: "#f59e0b",
        daily: toDailyCounts(stats.newBots),
      },
    ];
  }, [stats]);

  if (!stats) {
    return (
      <AdminStatsMessage>
        You do not have permission to view admin statistics.
      </AdminStatsMessage>
    );
  }

  const firstDate = series
    ? Math.min(...series.flatMap((s) => Array.from(s.daily.keys())))
    : Infinity;

  if (!series || !Number.isFinite(firstDate)) {
    return (
      <AdminStatsMessage>No admin statistics are available.</AdminStatsMessage>
    );
  }

  const unit = periodConfig.timeUnit;
  const periodStart = getPeriodStart(period);
  const buckets = createBuckets(periodStart ?? firstDate, unit);
  const daysInPeriod =
    (getTodayUtcTimestamp() - (periodStart ?? firstDate)) / DAY_IN_MS + 1;

  return (
    <AdminStatsChartSection
      type="bar"
      cards={series.map((s) => {
        const total = sumInPeriod(s.daily, periodStart);

        return {
          label: s.label,
          value: numberFormat.format(total),
          detail: `avg ${(total / daysInPeriod).toFixed(1)} / day`,
          color: s.color,
        };
      })}
      data={{
        datasets: series.map((s) =>
          barDataset(
            s.label,
            s.color,
            toBucketedSeries(buckets, s.daily, unit, periodStart),
          ),
        ),
      }}
      timeUnit={unit}
      yTitle={`New per ${unit}`}
      gridColor="rgba(134,194,50,0.12)"
    />
  );
}

export default function AdminStatsActivityTab() {
  return (
    <AdminStatsTabSuspense>
      <AdminStatsActivityTabContent />
    </AdminStatsTabSuspense>
  );
}
