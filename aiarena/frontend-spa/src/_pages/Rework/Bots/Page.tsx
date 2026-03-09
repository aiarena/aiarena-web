import { Suspense } from "react";

import Bots from "./Bots";
import DisplaySkeleton from "@/_components/_display/_skeletons/DisplaySkeleton";
import { SkeletonCardShadow } from "@/_components/_display/_skeletons/SkeletonCardShadow";

export default function BotsPage() {
  return (
    <Suspense
      fallback={<DisplaySkeleton height={600} styles={SkeletonCardShadow} />}
    >
      <Bots />
    </Suspense>
  );
}
