import { Suspense } from "react";
import Match from "./Match";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function MatchPage() {
  return (
    <div className="mb-8">
      <Suspense
        fallback={
          <div className="max-w-7xl mx-auto gap-8 grid">
            <DisplaySkeleton height={340} styles={SkeletonCardShadow} />
            <DisplaySkeleton height={450} styles={SkeletonCardShadow} />
            <DisplaySkeleton height={250} styles={SkeletonCardShadow} />
          </div>
        }
      >
        <ErrorBoundaryWrapper componentName="match">
          <Match />
        </ErrorBoundaryWrapper>
      </Suspense>
    </div>
  );
}
