import { useMemo } from "react";
import { graphql, useFragment, useLazyLoadQuery } from "react-relay";

import AdminStatsChartSection from "./AdminStatsChartSection";
import { AdminStatsMessage, AdminStatsTabSuspense } from "./AdminStatsMessage";
import {
  clipToPeriod,
  createDailyDateRange,
  getPeriodStart,
  lineDataset,
  numberFormat,
  sumInPeriod,
  toCumulativeSeries,
  toDailyCounts,
} from "./adminStatsSeries";
import useAdminStatsParams from "./useAdminStatsParams";
import { AdminStatsTotalsTabQuery } from "./__generated__/AdminStatsTotalsTabQuery.graphql";
import { AdminStatsTotalsTab_stats$key } from "./__generated__/AdminStatsTotalsTab_stats.graphql";

function AdminStatsTotalsTabContent() {
  const data = useLazyLoadQuery<AdminStatsTotalsTabQuery>(
    graphql`
      query AdminStatsTotalsTabQuery {
        statsForAdmins {
          ...AdminStatsTotalsTab_stats
        }
      }
    `,
    {},
    { fetchPolicy: "store-and-network" },
  );

  const stats = useFragment<AdminStatsTotalsTab_stats$key>(
    graphql`
      fragment AdminStatsTotalsTab_stats on StatsForAdmins {
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

    const raw = [
      { label: "Users", color: "#86c232", daily: toDailyCounts(stats.newUsers) },
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
      { label: "Bots", color: "#f59e0b", daily: toDailyCounts(stats.newBots) },
    ];

    const dates = createDailyDateRange(raw.map((s) => s.daily));

    return raw.map((s) => ({
      ...s,
      cumulative: toCumulativeSeries(dates, s.daily),
    }));
  }, [stats]);

  if (!stats) {
    return (
      <AdminStatsMessage>
        You do not have permission to view admin statistics.
      </AdminStatsMessage>
    );
  }

  if (!series || !series[0].cumulative.length) {
    return <AdminStatsMessage>No admin statistics are available.</AdminStatsMessage>;
  }

  const periodStart = getPeriodStart(period);
  const isAllTime = periodStart === null;

  return (
    <AdminStatsChartSection
      cards={series.map((s) => {
        const total = s.cumulative[s.cumulative.length - 1]?.y ?? 0;

        return {
          label: isAllTime ? s.label : `New ${s.label.toLowerCase()}`,
          value: numberFormat.format(sumInPeriod(s.daily, periodStart)),
          detail: isAllTime ? "All time" : `${numberFormat.format(total)} total`,
          color: s.color,
        };
      })}
      data={{
        datasets: series.map((s) =>
          lineDataset(
            `Total ${s.label.toLowerCase()}`,
            s.color,
            clipToPeriod(s.cumulative, periodStart),
          ),
        ),
      }}
      timeUnit={periodConfig.timeUnit}
      yTitle="Cumulative total"
      gridColor="rgba(134,194,50,0.12)"
    />
  );
}

export default function AdminStatsTotalsTab() {
  return (
    <AdminStatsTabSuspense>
      <AdminStatsTotalsTabContent />
    </AdminStatsTabSuspense>
  );
}
