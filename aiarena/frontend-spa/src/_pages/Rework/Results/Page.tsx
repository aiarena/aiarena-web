import { Suspense } from "react";
import Results from "./Results";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function ResultsPage() {
  return (
    <Suspense
      fallback={<DisplaySkeleton height={1600} styles={SkeletonCardShadow} />}
    >
      <ErrorBoundaryWrapper componentName="results">
        <Results />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
