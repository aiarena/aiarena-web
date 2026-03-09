import DisplaySkeleton from "./DisplaySkeleton";
import { SkeletonCardShadow } from "./SkeletonCardShadow";

export default function DisplaySkeletonUserBots() {
  return (
    <>
      <div className="grid gap-4">
        <DisplaySkeleton height={45} />
        <DisplaySkeleton height={500} styles={SkeletonCardShadow} />
      </div>
    </>
  );
}
