import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { Suspense } from "react";
import Competitions from "./Competitions";

export default function CompetitionsPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Competitions />
    </Suspense>
  );
}
