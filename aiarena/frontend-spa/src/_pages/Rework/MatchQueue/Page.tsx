import { Suspense } from "react";

import MatchQueue from "./MatchQueue";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function MatchQueuePage() {
  return (
    <div className="max-w-7xl mx-auto">
      <Suspense
        fallback={<DisplaySkeleton height={600} styles={SkeletonCardShadow} />}
      >
        <ErrorBoundaryWrapper componentName="match queue">
          <MatchQueue />
        </ErrorBoundaryWrapper>
      </Suspense>
    </div>
  );
}
