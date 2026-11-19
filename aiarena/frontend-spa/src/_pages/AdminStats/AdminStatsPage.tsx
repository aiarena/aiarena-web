import clsx from "clsx";

import ButtonToggle from "@/_components/_actions/_toggle/ButtonToggle";
import { STATS_PERIODS } from "./adminStatsSeries";
import AdminStatsActivityTab from "./AdminStatsActivityTab";
import AdminStatsPatreonTab from "./AdminStatsPatreonTab";
import AdminStatsPercentagesTab from "./AdminStatsPercentagesTab";
import AdminStatsTotalsTab from "./AdminStatsTotalsTab";
import useAdminStatsParams, { ADMIN_STATS_TABS } from "./useAdminStatsParams";

export default function AdminStatsPage() {
  const { period, setPeriod, tab, setTab } = useAdminStatsParams();

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-neutral-800 bg-darken-2 p-6 shadow-xl backdrop-blur-lg">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-neutral-100">Statistics</h2>

          <p className="mt-1 text-sm text-neutral-400">
            Usage, registrations, supporter activity, and platform statistics.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {STATS_PERIODS.map((p) => (
            <ButtonToggle
              key={p.value}
              text={p.label}
              active={p.value === period}
              onClick={() => setPeriod(p.value)}
            />
          ))}
        </div>
      </div>

      <nav className="flex overflow-x-auto border-b border-neutral-800">
        {ADMIN_STATS_TABS.map((t) => (
          <button
            key={t.value}
            type="button"
            onClick={() => setTab(t.value)}
            className={clsx(
              "relative whitespace-nowrap px-4 py-3 text-sm font-medium transition-colors",
              t.value === tab
                ? "text-white"
                : "text-neutral-400 hover:text-neutral-200",
            )}
          >
            {t.label}
            {t.value === tab && (
              <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-customGreen" />
            )}
          </button>
        ))}
      </nav>

      {tab === "totals" && <AdminStatsTotalsTab />}
      {tab === "activity" && <AdminStatsActivityTab />}
      {tab === "percentages" && <AdminStatsPercentagesTab />}
      {tab === "patreon" && <AdminStatsPatreonTab />}
    </div>
  );
}
