import { Suspense } from "react";

import AdminStats from "./AdminStats";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function AdminStatsPage() {
  return (
    <ErrorBoundaryWrapper>
      <Suspense fallback={<DisplaySkeleton height={558} />}>
        <div className="flex flex-col gap-6">
          <h1 className="text-2xl font-semibold text-neutral-100">
            Admin statistics
          </h1>

          <AdminStats />
        </div>
      </Suspense>
    </ErrorBoundaryWrapper>
  );
}
