import { Suspense } from "react";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import Rounds from "./Rounds";

export default function RoundsPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Rounds />
    </Suspense>
  );
}
