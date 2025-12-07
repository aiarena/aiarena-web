import Skeleton, { SkeletonTheme } from "react-loading-skeleton";

export default function DisplaySkeletonBlock({
  height = 300,
}: {
  height?: number;
}) {
  return (
    <SkeletonTheme baseColor="#18191E" highlightColor="#32333B">
      <p>
        <Skeleton height={height} />
      </p>
    </SkeletonTheme>
  );
}
