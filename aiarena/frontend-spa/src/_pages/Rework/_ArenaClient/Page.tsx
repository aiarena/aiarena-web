import { Suspense } from "react";

import ArenaClientSection from "./ArenaClientSection";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonBoxShadow } from "@/_components/_display/_skeletons/SkeletonBoxShadow";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function ArenaClientPage() {
  return (
    <div className="max-w-7xl mx-auto">
      <Suspense
        fallback={
          <>
            <div className="mb-8">
              <DisplaySkeleton height={180} styles={SkeletonBoxShadow} />
            </div>
            <div className="mb-8">
              <h4 className="mb-4">Assigned Matches</h4>
              <DisplaySkeleton height={80} styles={SkeletonCardShadow} />
            </div>
            <div className="mb-8">
              <h4 className="mb-4">Recent Results</h4>
              <DisplaySkeleton height={600} styles={SkeletonCardShadow} />
            </div>
          </>
        }
      >
        <ErrorBoundaryWrapper componentName="arena client">
          <ArenaClientSection />
        </ErrorBoundaryWrapper>
      </Suspense>
    </div>
  );
}
