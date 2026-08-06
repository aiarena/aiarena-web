import { getDotColor } from "@/_lib/getDotColor";

export function StatusBadge({ status }: { status: string | null | undefined }) {
  const dotColor = getDotColor(false, status?.toUpperCase() ?? "");

  const classNames: Record<string, string> = {
    green: "bg-[#86FE32] text-black",
    blue: "bg-[#3296FE] text-white",
    yellow: "bg-[#FEE632] text-black",
    gray: "bg-[#A0A0A0] text-black",
  };

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
        classNames[dotColor]
      }`}
    >
      {status ?? "Unknown"}
    </span>
  );
}

export function BooleanBadge({ value }: { value: boolean }) {
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
        value ? "bg-customgreen text-white" : "bg-red-500 text-white"
      }`}
    >
      {value ? "Yes" : "No"}
    </span>
  );
}

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

export function DateValue({ value }: { value: string | null | undefined }) {
  return <>{formatDate(value)}</>;
}

export function formatDate(value: string | null | undefined) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleDateString();
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleString();
}
