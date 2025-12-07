import Skeleton, { SkeletonTheme } from "react-loading-skeleton";

export default function DisplaySkeleton({
  height = undefined,
  count = undefined,
}: {
  height?: number;
  count?: number;
}) {
  return (
    <SkeletonTheme baseColor="#18191E" highlightColor="#32333B">
      <p>
        <Skeleton height={height} count={count} />
      </p>
    </SkeletonTheme>
  );
}
