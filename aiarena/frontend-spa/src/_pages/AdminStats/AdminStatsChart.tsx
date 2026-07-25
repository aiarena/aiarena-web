import { graphql, useFragment } from "react-relay";
import { useMemo } from "react";

import {
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  TimeScale,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";
import "chartjs-adapter-date-fns";

import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import { AdminStatsChart_node$key } from "./__generated__/AdminStatsChart_node.graphql";

interface AdminStatsChartProps {
  data: AdminStatsChart_node$key;
}

type StatsPoint = {
  readonly dateTime: string;
  readonly count: number;
};

type ChartPoint = {
  x: number;
  y: number;
};

const DAY_IN_MS = 24 * 60 * 60 * 1000;

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  Filler,
);

function toUtcDayTimestamp(value: string): number | null {
  const normalized = /^\d{4}-\d{2}-\d{2}$/.test(value)
    ? `${value}T00:00:00.000Z`
    : value;

  const date = new Date(normalized);

  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
}

function toDailyCounts(
  points: readonly (StatsPoint | null | undefined)[],
): Map<number, number> {
  const counts = new Map<number, number>();

  for (const point of points) {
    if (!point) continue;
    const timestamp = toUtcDayTimestamp(point.dateTime);

    if (timestamp === null) {
      continue;
    }

    counts.set(timestamp, (counts.get(timestamp) ?? 0) + point.count);
  }

  return counts;
}

function getTodayUtcTimestamp(): number {
  const now = new Date();

  return Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
}

function createDailyDateRange(timestamps: readonly number[]): number[] {
  if (!timestamps.length) {
    return [];
  }

  const firstDate = Math.min(...timestamps);

  const finalDate = Math.max(Math.max(...timestamps), getTodayUtcTimestamp());

  const dates: number[] = [];

  for (
    let timestamp = firstDate;
    timestamp <= finalDate;
    timestamp += DAY_IN_MS
  ) {
    dates.push(timestamp);
  }

  return dates;
}

function toCumulativeSeries(
  dates: readonly number[],
  dailyCounts: ReadonlyMap<number, number>,
): ChartPoint[] {
  let total = 0;

  return dates.map((date) => {
    total += dailyCounts.get(date) ?? 0;

    return {
      x: date,
      y: total,
    };
  });
}

function toPercentageSeries(
  dates: readonly number[],
  numeratorDailyCounts: ReadonlyMap<number, number>,
  totalUsersDailyCounts: ReadonlyMap<number, number>,
): ChartPoint[] {
  let numeratorTotal = 0;
  let totalUsers = 0;

  return dates.map((date) => {
    numeratorTotal += numeratorDailyCounts.get(date) ?? 0;

    totalUsers += totalUsersDailyCounts.get(date) ?? 0;

    return {
      x: date,
      y: totalUsers > 0 ? (numeratorTotal / totalUsers) * 100 : 0,
    };
  });
}

const sharedChartOptions = {
  animation: false as const,
  responsive: true,
  maintainAspectRatio: false,
  parsing: false as const,
  normalized: true,
  interaction: {
    mode: "nearest" as const,
    axis: "x" as const,
    intersect: false,
  },
};

export default function AdminStatsChart(props: AdminStatsChartProps) {
  const stats = useFragment(
    graphql`
      fragment AdminStatsChart_node on StatsForAdmins {
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

        newBots {
          dateTime
          count
        }
      }
    `,
    props.data,
  );

  const charts = useMemo(() => {
    const usersByDate = toDailyCounts(stats.newUsers);

    const usersWithBotsByDate = toDailyCounts(stats.newUsersWithAtLeastOneBot);

    const patreonUsersByDate = toDailyCounts(stats.newPatreonUsers);

    const bronzePledgeByDate = toDailyCounts(stats.bronzePatreonPledge);

    const silverPledgeByDate = toDailyCounts(stats.silverPatreonPledge);

    const goldPledgeByDate = toDailyCounts(stats.goldPatreonPledge);

    const platinumPledgeByDate = toDailyCounts(stats.platinumPatreonPledge);

    const diamondPledgeByDate = toDailyCounts(stats.diamondPatreonPledge);

    const botsByDate = toDailyCounts(stats.newBots);

    const datesWithData = Array.from(
      new Set([
        ...usersByDate.keys(),
        ...usersWithBotsByDate.keys(),
        ...patreonUsersByDate.keys(),
        ...bronzePledgeByDate.keys(),
        ...silverPledgeByDate.keys(),
        ...goldPledgeByDate.keys(),
        ...platinumPledgeByDate.keys(),
        ...diamondPledgeByDate.keys(),
        ...botsByDate.keys(),
      ]),
    );

    const dates = createDailyDateRange(datesWithData);

    if (!dates.length) {
      return null;
    }

    const cumulativeUsers = toCumulativeSeries(dates, usersByDate);

    const cumulativeUsersWithBots = toCumulativeSeries(
      dates,
      usersWithBotsByDate,
    );

    const cumulativePatreonUsers = toCumulativeSeries(
      dates,
      patreonUsersByDate,
    );

    const cumulativeBots = toCumulativeSeries(dates, botsByDate);

    const usersWithBotsPercentage = toPercentageSeries(
      dates,
      usersWithBotsByDate,
      usersByDate,
    );

    const patreonUsersPercentage = toPercentageSeries(
      dates,
      patreonUsersByDate,
      usersByDate,
    );
    const cumulativeBronzePledge = toCumulativeSeries(
      dates,
      bronzePledgeByDate,
    );

    const cumulativeSilverPledge = toCumulativeSeries(
      dates,
      silverPledgeByDate,
    );

    const cumulativeGoldPledge = toCumulativeSeries(dates, goldPledgeByDate);

    const cumulativePlatinumPledge = toCumulativeSeries(
      dates,
      platinumPledgeByDate,
    );

    const cumulativeDiamondPledge = toCumulativeSeries(
      dates,
      diamondPledgeByDate,
    );

    return {
      totals: {
        datasets: [
          {
            label: "Total users",
            data: cumulativeUsers,
            borderColor: "#86c232",
            backgroundColor: "#86c232",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
          },
          {
            label: "Total users with a bot",
            data: cumulativeUsersWithBots,
            borderColor: "#38bdf8",
            backgroundColor: "#38bdf8",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
          },
          {
            label: "Total Patreon donators",
            data: cumulativePatreonUsers,
            borderColor: "#f472b6",
            backgroundColor: "#f472b6",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
          },
          {
            label: "Total bots",
            data: cumulativeBots,
            borderColor: "#f59e0b",
            backgroundColor: "#f59e0b",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
          },
        ],
      },

      percentages: {
        datasets: [
          {
            label: "Users with a bot",
            data: usersWithBotsPercentage,
            borderColor: "#38bdf8",
            backgroundColor: "#38bdf8",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
          },
          {
            label: "Patreon donators",
            data: patreonUsersPercentage,
            borderColor: "#f472b6",
            backgroundColor: "#f472b6",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
          },
        ],
      },

      pledge: {
        datasets: [
          {
            label: "Bronze",
            data: cumulativeBronzePledge,
            borderColor: "#cd7f32",
            backgroundColor: "rgba(205, 127, 50, 0.35)",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
            fill: true,
            stack: "patreon",
          },
          {
            label: "Silver",
            data: cumulativeSilverPledge,
            borderColor: "#c0c0c0",
            backgroundColor: "rgba(192, 192, 192, 0.35)",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
            fill: true,
            stack: "patreon",
          },
          {
            label: "Gold",
            data: cumulativeGoldPledge,
            borderColor: "#f59e0b",
            backgroundColor: "rgba(245, 158, 11, 0.35)",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
            fill: true,
            stack: "patreon",
          },
          {
            label: "Platinum",
            data: cumulativePlatinumPledge,
            borderColor: "#67e8f9",
            backgroundColor: "rgba(103, 232, 249, 0.35)",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
            fill: true,
            stack: "patreon",
          },
          {
            label: "Diamond",
            data: cumulativeDiamondPledge,
            borderColor: "#a78bfa",
            backgroundColor: "rgba(167, 139, 250, 0.35)",
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2,
            stepped: "after" as const,
            fill: true,
            stack: "patreon",
          },
        ],
      },
    };
  }, [
    stats.newUsers,
    stats.newUsersWithAtLeastOneBot,
    stats.newPatreonUsers,
    stats.bronzePatreonPledge,
    stats.silverPatreonPledge,
    stats.goldPatreonPledge,
    stats.platinumPatreonPledge,
    stats.diamondPatreonPledge,
    stats.newBots,
  ]);

  if (!charts) {
    return (
      <div
        className="flex items-center justify-center rounded-xl border border-neutral-800 bg-darken-2 p-4 shadow-lg backdrop-blur-lg"
        style={{ height: 558 }}
      >
        <NoItemsInListMessage>
          <p>No admin statistics are available.</p>
        </NoItemsInListMessage>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="mb-3 text-lg font-semibold text-neutral-100">
          Cumulative totals
        </h2>

        <div
          className="rounded-xl border border-neutral-800 bg-darken-2 p-4 pt-6 shadow-lg backdrop-blur-lg"
          style={{ height: 558 }}
        >
          <Line
            data={charts.totals}
            options={{
              ...sharedChartOptions,

              scales: {
                x: {
                  type: "time",
                  time: {
                    unit: "day",
                    tooltipFormat: "PP",
                  },
                  ticks: {
                    color: "#f3f4f6",
                    maxRotation: 0,
                    autoSkip: true,
                  },
                  grid: {
                    color: "rgba(134,194,50,0.12)",
                  },
                  title: {
                    display: true,
                    text: "Date",
                    color: "#f3f4f6",
                  },
                },

                y: {
                  beginAtZero: true,
                  ticks: {
                    color: "#f3f4f6",
                    precision: 0,
                  },
                  grid: {
                    color: "rgba(134,194,50,0.12)",
                  },
                  title: {
                    display: true,
                    text: "Cumulative total",
                    color: "#f3f4f6",
                  },
                },
              },

              plugins: {
                datalabels: {
                  display: false,
                },

                legend: {
                  display: true,
                  labels: {
                    color: "#f3f4f6",
                    usePointStyle: true,
                    boxWidth: 8,
                  },
                },

                tooltip: {
                  mode: "index",
                  intersect: false,
                },
              },
            }}
          />
        </div>
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold text-neutral-100">
          Percentage of total users
        </h2>

        <div
          className="rounded-xl border border-neutral-800 bg-darken-2 p-4 pt-6 shadow-lg backdrop-blur-lg"
          style={{ height: 558 }}
        >
          <Line
            data={charts.percentages}
            options={{
              ...sharedChartOptions,

              scales: {
                x: {
                  type: "time",
                  time: {
                    unit: "day",
                    tooltipFormat: "PP",
                  },
                  ticks: {
                    color: "#f3f4f6",
                    maxRotation: 0,
                    autoSkip: true,
                  },
                  grid: {
                    color: "rgba(134,194,50,0.12)",
                  },
                  title: {
                    display: true,
                    text: "Date",
                    color: "#f3f4f6",
                  },
                },

                y: {
                  beginAtZero: true,
                  max: 100,
                  ticks: {
                    color: "#f3f4f6",
                    callback(value) {
                      return `${value}%`;
                    },
                  },
                  grid: {
                    color: "rgba(134,194,50,0.12)",
                  },
                  title: {
                    display: true,
                    text: "Percentage of total users",
                    color: "#f3f4f6",
                  },
                },
              },

              plugins: {
                datalabels: {
                  display: false,
                },

                legend: {
                  display: true,
                  labels: {
                    color: "#f3f4f6",
                    usePointStyle: true,
                    boxWidth: 8,
                  },
                },

                tooltip: {
                  mode: "index",
                  intersect: false,
                  callbacks: {
                    label(context) {
                      const value = context.parsed.y ?? 0;

                      return `${context.dataset.label}: ${value.toFixed(2)}%`;
                    },
                  },
                },
              },
            }}
          />
        </div>
      </div>
      <div>
        <h2 className="mb-3 text-lg font-semibold text-neutral-100">
          Total Patreon pledge
        </h2>
        <p>
          Large discrepancy between these stats and ground truth. Housebots,
          etc, are included.{" "}
        </p>
        <div
          className="rounded-xl border border-neutral-800 bg-darken-2 p-4 pt-6 shadow-lg backdrop-blur-lg"
          style={{ height: 558 }}
        >
          <Line
            data={charts.pledge}
            options={{
              ...sharedChartOptions,

              scales: {
                x: {
                  type: "time",
                  stacked: true,
                  time: {
                    unit: "day",
                    tooltipFormat: "PP",
                  },
                  ticks: {
                    color: "#f3f4f6",
                    maxRotation: 0,
                    autoSkip: true,
                  },
                  grid: {
                    color: "rgba(167,139,250,0.12)",
                  },
                  title: {
                    display: true,
                    text: "Date",
                    color: "#f3f4f6",
                  },
                },

                y: {
                  beginAtZero: true,
                  stacked: true,
                  ticks: {
                    color: "#f3f4f6",
                    callback(value) {
                      return `$${value}`;
                    },
                  },
                  grid: {
                    color: "rgba(167,139,250,0.12)",
                  },
                  title: {
                    display: true,
                    text: "Monthly pledge",
                    color: "#f3f4f6",
                  },
                },
              },
              plugins: {
                datalabels: {
                  display: false,
                },

                legend: {
                  display: true,
                  labels: {
                    color: "#f3f4f6",
                    usePointStyle: true,
                    boxWidth: 8,
                  },
                },

                tooltip: {
                  mode: "index",
                  intersect: false,
                  callbacks: {
                    label(context) {
                      const value = context.parsed.y ?? 0;

                      return `${context.dataset.label}: $${value.toFixed(2)}/month`;
                    },

                    footer(tooltipItems) {
                      const total = tooltipItems.reduce(
                        (sum, item) => sum + (item.parsed.y ?? 0),
                        0,
                      );

                      return `Total: $${total.toFixed(2)}/month`;
                    },
                  },
                },
              },
            }}
          />
        </div>
      </div>
    </div>
  );
}
