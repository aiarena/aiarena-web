import { ReactNode } from "react";

export default function NoItemsInListMessage({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="flex items-center justify-center min-h-[40vh] text-center">
      {children}
    </div>
  );
}
