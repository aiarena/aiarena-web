import { ReactNode, Suspense } from "react";

import NoItemsInListMessage from "@/_components/_display/NoItemsInListMessage";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";

export function AdminStatsMessage({ children }: { children: ReactNode }) {
  return (
    <div
      className="flex items-center justify-center rounded-xl border border-neutral-800 bg-darken-2 p-4 shadow-lg backdrop-blur-lg"
      style={{ height: 558 }}
    >
      <NoItemsInListMessage>
        <p>{children}</p>
      </NoItemsInListMessage>
    </div>
  );
}

/**
 * Each statistics tab runs its own query below this boundary, so switching
 * tabs shows this skeleton instead of leaving the previous tab on screen.
 */
export function AdminStatsTabSuspense({ children }: { children: ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col gap-4">
          <DisplaySkeleton height={84} />
          <DisplaySkeleton height={558} />
        </div>
      }
    >
      {children}
    </Suspense>
  );
}
