import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import { Suspense } from "react";
import AuthorSection from "./AuthorSection";

export default function AuthorPage() {
  return (
    <Suspense fallback={<LoadingSpinner color="light-gray" />}>
      <AuthorSection />
    </Suspense>
  );
}
