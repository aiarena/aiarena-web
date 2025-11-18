import { Suspense } from "react";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import Competition from "./Competition";

export default function CompetitionPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Competition />
    </Suspense>
  );
}
