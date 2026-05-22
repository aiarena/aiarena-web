import { Suspense } from "react";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import Developers from "./Developers";

export default function DevelopersPage() {
  return (
    <Suspense
      fallback={
        <div className="flex justify-center py-20">
          <LoadingSpinner />
        </div>
      }
    >
      <ErrorBoundaryWrapper componentName="developers">
        <Developers />
      </ErrorBoundaryWrapper>
    </Suspense>
  );
}
