import Skeleton, { SkeletonTheme } from "react-loading-skeleton";

export default function DisplaySkeleton({
  height = undefined,
  count = undefined,
}: {
  height?: number;
  count?: number;
}) {
  return (
    <SkeletonTheme baseColor="#18191E" highlightColor="#22232B">
      <p>
        <Skeleton
          height={height}
          count={count}
          customHighlightBackground="
            linear-gradient(
              90deg,
              var(--base-color) 30%,
              var(--highlight-color) 50%,
              var(--base-color) 70%
            )
          "
        />
      </p>
    </SkeletonTheme>
  );
}
