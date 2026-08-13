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
