import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { Suspense } from "react";
import Authors from "./Authors";

export default function AuthorsPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <Authors />
    </Suspense>
  );
}
