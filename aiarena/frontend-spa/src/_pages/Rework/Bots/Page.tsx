import { Suspense } from "react";

import Bots from "./Bots";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function BotsPage() {
  return (
    <Suspense
      fallback={<DisplaySkeleton height={600} styles={SkeletonCardShadow} />}
    >
      <ErrorBoundaryWrapper componentName="bots">
        <Bots />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
