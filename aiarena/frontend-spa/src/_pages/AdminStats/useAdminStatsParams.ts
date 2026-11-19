import { useSearchParams } from "react-router";

import { STATS_PERIODS, StatsPeriod } from "./adminStatsSeries";

export const ADMIN_STATS_TABS = [
  { value: "totals", label: "Totals" },
  { value: "activity", label: "Activity" },
  { value: "percentages", label: "Percentages" },
  { value: "patreon", label: "Patreon pledge" },
] as const;

export type AdminStatsTab = (typeof ADMIN_STATS_TABS)[number]["value"];

/**
 * The selected tab and period live in search params (`?tab=&period=`), not the
 * path: they're views of one dataset, so switching them shouldn't count as a
 * page navigation (which would scroll to top). Both survive refreshes and links.
 */
export default function useAdminStatsParams() {
  const [searchParams, setSearchParams] = useSearchParams();

  const periodConfig =
    STATS_PERIODS.find((p) => p.value === searchParams.get("period")) ??
    STATS_PERIODS.find((p) => p.value === "all") ??
    STATS_PERIODS[0];

  const tab =
    ADMIN_STATS_TABS.find((t) => t.value === searchParams.get("tab"))?.value ??
    ADMIN_STATS_TABS[0].value;

  const setParam = (key: string, value: string) =>
    setSearchParams(
      (params) => {
        params.set(key, value);
        return params;
      },
      { replace: true },
    );

  return {
    period: periodConfig.value,
    periodConfig,
    setPeriod: (period: StatsPeriod) => setParam("period", period),
    tab,
    setTab: (next: AdminStatsTab) => setParam("tab", next),
  };
}
