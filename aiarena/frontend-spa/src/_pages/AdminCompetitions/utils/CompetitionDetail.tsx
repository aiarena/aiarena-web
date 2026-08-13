export function CompetitionDetail({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-neutral-500">
        {label}
      </dt>

      <dd className="mt-2 text-sm text-neutral-100">{value}</dd>
    </div>
  );
}
