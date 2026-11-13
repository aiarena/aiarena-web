import { Suspense } from "react";

import ArenaClients from "./ArenaClients";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function ArenaClientsPage() {
  return (
    <Suspense
      fallback={<DisplaySkeleton height={400} styles={SkeletonCardShadow} />}
    >
      <ErrorBoundaryWrapper componentName="arena clients">
        <ArenaClients />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
