import { Suspense } from "react";
import AuthorSection from "./AuthorSection";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";
import { SkeletonBoxShadow } from "@/_components/_display/_skeletons/SkeletonBoxShadow";
import ErrorBoundaryWrapper from "@/_lib/ErrorBoundary";

export default function AuthorPage() {
  return (
    <div className="max-w-7xl mx-auto">
      <Suspense
        fallback={
          <div className="grid gap-8">
            <DisplaySkeleton height={190} styles={SkeletonBoxShadow} />
            <DisplaySkeleton height={200} styles={SkeletonCardShadow} />
          </div>
        }
      >
        <ErrorBoundaryWrapper componentName="author">
          <AuthorSection />
        </ErrorBoundaryWrapper>
      </Suspense>
    </div>
  );
}
