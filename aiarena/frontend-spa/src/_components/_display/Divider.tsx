import clsx from "clsx";

interface DividerProps {
  label: string;
  labelPlacement: "left" | "center" | "right";
  className?: string;
}

export default function Divider({
  label,
  labelPlacement = "center",
  className = "",
}: DividerProps) {
  const alignment =
    labelPlacement === "left"
      ? "justify-start"
      : labelPlacement === "right"
        ? "justify-end"
        : "justify-center";

  return (
    <div className={clsx("flex items-center w-full", alignment, className)}>
      <div className="flex-1 h-[1px] bg-gray-500" />
      {label && (
        <span
          className={clsx(
            "mx-3 text-sm whitespace-nowrap",
            labelPlacement === "left" && "order-first"
          )}
        >
          {label}
        </span>
      )}
      <div className="flex-1 h-[1px] bg-gray-500" />
    </div>
  );
}
