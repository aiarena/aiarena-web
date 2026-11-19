import { Suspense } from "react";
import Competition from "./Competition";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";

export default function CompetitionPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Competition />
    </Suspense>
  );
}
