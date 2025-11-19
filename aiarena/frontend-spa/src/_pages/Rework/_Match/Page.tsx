import { Suspense } from "react";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import Match from "./Match";

export default function MatchPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Match />
    </Suspense>
  );
}
