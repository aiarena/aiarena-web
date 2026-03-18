import { Suspense } from "react";
import Rounds from "./Rounds";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";

export default function RoundsPage() {
  return (
    <Suspense
      fallback={
        <div className="grid gap-7">
          <DisplaySkeleton height={205} styles={SkeletonCardShadow} />
          <DisplaySkeleton height={1200} styles={SkeletonCardShadow} />
        </div>
      }
    >
      <Rounds />
    </Suspense>
  );
}
