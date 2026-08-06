import { Suspense } from "react";

import AdminCompetitions from "./AdminCompetitions";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function AdminCompetitionsPage() {
  return (
    <ErrorBoundaryWrapper>
      <Suspense fallback={<DisplaySkeleton height={558} />}>
        <div className="flex flex-col gap-6">
          <div>
            <h1 className="text-2xl font-semibold text-neutral-100">
              Competition awards
            </h1>

            <p className="mt-1 text-sm text-neutral-400">
              Check and award trophies for configured competitions.
            </p>
          </div>

          <AdminCompetitions />
        </div>
      </Suspense>
    </ErrorBoundaryWrapper>
  );
}
