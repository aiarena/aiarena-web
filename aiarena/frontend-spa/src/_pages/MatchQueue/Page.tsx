import { Suspense } from "react";

import MatchQueue from "./MatchQueue";
import MatchQueueSkeleton from "./MatchQueueSkeleton";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function MatchQueuePage() {
  return (
    <div className="max-w-7xl mx-auto">
      <Suspense fallback={<MatchQueueSkeleton />}>
        <ErrorBoundaryWrapper componentName="match queue">
          <MatchQueue />
        </ErrorBoundaryWrapper>
      </Suspense>
    </div>
  );
}
