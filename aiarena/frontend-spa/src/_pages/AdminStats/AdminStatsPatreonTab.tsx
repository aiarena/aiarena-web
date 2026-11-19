import { useMemo } from "react";
import { graphql, useFragment, useLazyLoadQuery } from "react-relay";

import AdminStatsChartSection from "./AdminStatsChartSection";
import { AdminStatsMessage, AdminStatsTabSuspense } from "./AdminStatsMessage";
import {
  clipToPeriod,
  createDailyDateRange,
  getPeriodStart,
  numberFormat,
  stackedDataset,
  sumInPeriod,
  toCumulativeSeries,
  toDailyCounts,
} from "./adminStatsSeries";
import useAdminStatsParams from "./useAdminStatsParams";
import { AdminStatsPatreonTabQuery } from "./__generated__/AdminStatsPatreonTabQuery.graphql";
import { AdminStatsPatreonTab_stats$key } from "./__generated__/AdminStatsPatreonTab_stats.graphql";

function AdminStatsPatreonTabContent() {
  const data = useLazyLoadQuery<AdminStatsPatreonTabQuery>(
    graphql`
      query AdminStatsPatreonTabQuery {
        statsForAdmins {
          ...AdminStatsPatreonTab_stats
        }
      }
    `,
    {},
    { fetchPolicy: "store-and-network" },
  );

  const stats = useFragment<AdminStatsPatreonTab_stats$key>(
    graphql`
      fragment AdminStatsPatreonTab_stats on StatsForAdmins {
        bronzePatreonPledge {
          dateTime
          count
        }
        silverPatreonPledge {
          dateTime
          count
        }
        goldPatreonPledge {
          dateTime
          count
        }
        platinumPatreonPledge {
          dateTime
          count
        }
        diamondPatreonPledge {
          dateTime
          count
        }
      }
    `,
    data.statsForAdmins,
  );

  const { period, periodConfig } = useAdminStatsParams();

  const tiers = useMemo(() => {
    if (!stats) return null;

    const raw = [
      {
        label: "Bronze",
        color: "#cd7f32",
        fill: "rgba(205, 127, 50, 0.35)",
        daily: toDailyCounts(stats.bronzePatreonPledge),
      },
      {
        label: "Silver",
        color: "#c0c0c0",
        fill: "rgba(192, 192, 192, 0.35)",
        daily: toDailyCounts(stats.silverPatreonPledge),
      },
      {
        label: "Gold",
        color: "#f59e0b",
        fill: "rgba(245, 158, 11, 0.35)",
        daily: toDailyCounts(stats.goldPatreonPledge),
      },
      {
        label: "Platinum",
        color: "#67e8f9",
        fill: "rgba(103, 232, 249, 0.35)",
        daily: toDailyCounts(stats.platinumPatreonPledge),
      },
      {
        label: "Diamond",
        color: "#a78bfa",
        fill: "rgba(167, 139, 250, 0.35)",
        daily: toDailyCounts(stats.diamondPatreonPledge),
      },
    ];

    const dates = createDailyDateRange(raw.map((t) => t.daily));

    return raw.map((t) => ({
      ...t,
      cumulative: toCumulativeSeries(dates, t.daily),
    }));
  }, [stats]);

  if (!stats) {
    return (
      <AdminStatsMessage>
        You do not have permission to view admin statistics.
      </AdminStatsMessage>
    );
  }

  if (!tiers || !tiers[0].cumulative.length) {
    return <AdminStatsMessage>No Patreon statistics are available.</AdminStatsMessage>;
  }

  const periodStart = getPeriodStart(period);
  const amounts = tiers.map((t) => sumInPeriod(t.daily, periodStart));
  const totalAmount = amounts.reduce((sum, amount) => sum + amount, 0);

  return (
    <AdminStatsChartSection
      description="Large discrepancy between these stats and ground truth. Housebots, etc, are included."
      cards={[
        ...tiers.map((t, i) => ({
          label: t.label,
          value: `$${numberFormat.format(amounts[i])}`,
          detail: "/month",
          color: t.color,
        })),
        {
          label: "Total",
          value: `$${numberFormat.format(totalAmount)}`,
          detail: "/month",
          color: "#f3f4f6",
        },
      ]}
      data={{
        datasets: tiers.map((t) =>
          stackedDataset(
            t.label,
            t.color,
            t.fill,
            clipToPeriod(t.cumulative, periodStart),
          ),
        ),
      }}
      timeUnit={periodConfig.timeUnit}
      yTitle="Monthly pledge"
      gridColor="rgba(167,139,250,0.12)"
      stacked
      formatTick={(value) => `$${value}`}
      formatTooltipLabel={(item) =>
        `${item.dataset.label}: $${(item.parsed.y ?? 0).toFixed(2)}/month`
      }
      formatTooltipFooter={(items) =>
        `Total: $${items
          .reduce((sum, item) => sum + (item.parsed.y ?? 0), 0)
          .toFixed(2)}/month`
      }
    />
  );
}

export default function AdminStatsPatreonTab() {
  return (
    <AdminStatsTabSuspense>
      <AdminStatsPatreonTabContent />
    </AdminStatsTabSuspense>
  );
}
