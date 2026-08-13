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
