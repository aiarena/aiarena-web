import { Suspense } from "react";
import Results from "./Results";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";

export default function ResultsPage() {
  return (
    <Suspense
      fallback={<DisplaySkeletonTable columns={7} rows={20} />}
    >
      <ErrorBoundaryWrapper componentName="results">
        <Results />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
