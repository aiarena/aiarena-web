import { Suspense } from "react";
import CompetitionInformation from "./CompetitionInformation";
import CompetitionRankings from "./CompetitionRankings";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function Competition() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h4 className="mb-4">Competition</h4>
        <Suspense
          fallback={
            <DisplaySkeleton height={600} styles={SkeletonCardShadow} />
          }
        >
          <ErrorBoundaryWrapper componentName="competition information">
            <CompetitionInformation />
          </ErrorBoundaryWrapper>
        </Suspense>
      </div>
      <div className="mb-8">
        <h4 className="mb-4">Rankings</h4>
        <Suspense
          fallback={
            <DisplaySkeleton height={1600} styles={SkeletonCardShadow} />
          }
        >
          <ErrorBoundaryWrapper componentName="competition rankings">
            <CompetitionRankings />
          </ErrorBoundaryWrapper>
        </Suspense>
      </div>
    </div>
  );
}
