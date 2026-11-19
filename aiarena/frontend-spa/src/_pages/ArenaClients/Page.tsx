import { Suspense } from "react";

import ArenaClients from "./ArenaClients";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";
import DisplaySkeletonTable from "@/_components/_display/_skeletons/DisplaySkeletonTable";

export default function ArenaClientsPage() {
  return (
    <Suspense
      fallback={<DisplaySkeletonTable columns={4} rows={20} />}
    >
      <ErrorBoundaryWrapper componentName="arena clients">
        <ArenaClients />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
