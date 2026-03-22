import { Suspense } from "react";
import Rounds from "./Rounds";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function RoundsPage() {
  return (
    <Suspense
      fallback={
        <div className="grid gap-7">
          <DisplaySkeleton height={205} styles={SkeletonCardShadow} />
          <DisplaySkeleton height={1200} styles={SkeletonCardShadow} />
        </div>
      }
    >
      <ErrorBoundaryWrapper componentName="rounds">
        <Rounds />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
