import { ReactNode } from "react";
import clsx from "clsx";

export default function NoItemsInListMessage({
  children,
  height = "40vh",
  className,
}: {
  children: ReactNode;
  height?: string;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        "flex items-center justify-center text-center",
        `min-h-[${height}]`,
        className,
      )}
    >
      {children}
    </div>
  );
}
