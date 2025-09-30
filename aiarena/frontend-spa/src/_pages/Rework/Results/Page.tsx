import { Suspense } from "react";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import Results from "./Results";

export default function ResultsPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Results />
    </Suspense>
  );
}
