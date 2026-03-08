import { CSSProperties } from "react";
import Skeleton, { SkeletonTheme } from "react-loading-skeleton";
export default function DisplaySkeleton({
  height = undefined,
  width = undefined,
  count = undefined,
  styles,
  circle,
}: {
  height?: number;
  width?: number;
  count?: number;
  circle?: boolean;
  styles?: CSSProperties;
}) {
  return (
    <SkeletonTheme baseColor="#18191E" highlightColor="#22232B">
      <p>
        <Skeleton
          height={height}
          width={width}
          count={count}
          circle={circle}
          style={styles}
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
