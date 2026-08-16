import AdminStats from "./AdminStats";

export default function AdminStatsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold text-neutral-100">Statistics</h2>

        <p className="mt-1 text-sm text-neutral-400">
          Usage, registrations, supporter activity, and platform statistics.
        </p>
      </div>

      <AdminStats />
    </div>
  );
}
