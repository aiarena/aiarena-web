import DisplaySkeleton from "./DisplaySkeleton";
import { SkeletonCardShadow } from "./SkeletonCardShadow";

export default function DisplaySkeletonRequestMatches() {
  return (
    <>
      <div className="grid gap-4">
        <DisplaySkeleton height={45} />
        <DisplaySkeleton height={1200} styles={SkeletonCardShadow} />
      </div>
    </>
  );
}
