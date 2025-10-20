import { Suspense } from "react";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import Bots from "./Bots";

export default function BotsPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Bots />
    </Suspense>
  );
}
