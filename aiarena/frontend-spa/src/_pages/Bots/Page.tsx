import { Suspense } from "react";

import Bots from "./Bots";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";

export default function BotsPage() {
  return (
    <Suspense
      fallback={<DisplaySkeletonTable columns={5} rows={20} />}
    >
      <ErrorBoundaryWrapper componentName="bots">
        <Bots />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
